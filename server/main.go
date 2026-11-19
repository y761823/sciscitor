package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/Microsoft/go-winio"
)

// version is injected at build time via
// -ldflags "-X main.version=<project version>"
var version = "dev"

const (
	// The server talks to an OpenAI-compatible endpoint. Ollama exposes one
	// under /v1; switching to another provider only requires changing this URL.
	chatCompletionsURL = "http://127.0.0.1:11434/v1/chat/completions"
	defaultModel       = "qwen3:14b"

	upstreamTimeout      = 300 * time.Second
	requestReadTimeout   = 30 * time.Second
	responseWriteTimeout = upstreamTimeout + requestReadTimeout

	// maxFrameSize is far more than any prompt we accept; it only guards
	// against a corrupt length prefix.
	maxFrameSize   = 1 << 20
	maxErrorDetail = 512
)

// request is the single frame a client sends over the pipe.
type request struct {
	Prompt string `json:"prompt"`
	Model  string `json:"model"`
}

// response is the single frame the server writes back.
type response struct {
	Text  string `json:"text,omitempty"`
	Error string `json:"error,omitempty"`
}

type chatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type chatRequest struct {
	Model    string        `json:"model"`
	Messages []chatMessage `json:"messages"`
	Stream   bool          `json:"stream"`
}

type chatResponse struct {
	Choices []struct {
		Message chatMessage `json:"message"`
	} `json:"choices"`
}

func main() {
	pipeName := flag.String("pipe", "", "named pipe to listen on")
	showVersion := flag.Bool("version", false, "print version and exit")
	flag.Parse()

	if *showVersion {
		fmt.Println(version)
		return
	}

	if *pipeName == "" {
		fmt.Fprintln(os.Stderr, "sciscitor-server: --pipe is required")
		os.Exit(2)
	}

	listener, err := winio.ListenPipe(`\\.\pipe\`+*pipeName, nil)
	if err != nil {
		fmt.Fprintf(os.Stderr, "sciscitor-server: listen on %s: %v\n", *pipeName, err)
		os.Exit(1)
	}
	defer listener.Close()

	fmt.Printf("sciscitor-server %s listening on %s\n", version, *pipeName)

	client := &http.Client{Timeout: upstreamTimeout}
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Fprintf(os.Stderr, "sciscitor-server: accept: %v\n", err)
			return
		}
		go serveConn(conn, client)
	}
}

// serveConn handles exactly one request/response exchange and then closes the
// connection: the client opens a fresh pipe instance for every prompt.
func serveConn(conn net.Conn, client *http.Client) {
	defer conn.Close()

	_ = conn.SetReadDeadline(time.Now().Add(requestReadTimeout))

	var req request
	if err := readFrame(conn, &req); err != nil {
		fmt.Fprintf(os.Stderr, "sciscitor-server: read request: %v\n", err)
		return
	}

	resp := response{}
	if text, err := complete(client, req); err != nil {
		resp.Error = err.Error()
	} else {
		resp.Text = text
	}

	_ = conn.SetWriteDeadline(time.Now().Add(responseWriteTimeout))
	if err := writeFrame(conn, resp); err != nil {
		fmt.Fprintf(os.Stderr, "sciscitor-server: write response: %v\n", err)
	}
}

func complete(client *http.Client, req request) (string, error) {
	prompt := strings.TrimSpace(req.Prompt)
	if prompt == "" {
		return "", errors.New("prompt is empty")
	}

	model := strings.TrimSpace(req.Model)
	if model == "" {
		model = defaultModel
	}

	payload, err := json.Marshal(chatRequest{
		Model:    model,
		Messages: []chatMessage{{Role: "user", Content: prompt}},
	})
	if err != nil {
		return "", fmt.Errorf("encode request: %w", err)
	}

	httpReq, err := http.NewRequest(http.MethodPost, chatCompletionsURL, bytes.NewReader(payload))
	if err != nil {
		return "", fmt.Errorf("build request: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")

	httpResp, err := client.Do(httpReq)
	if err != nil {
		return "", fmt.Errorf("call model endpoint: %w", err)
	}
	defer httpResp.Body.Close()

	if httpResp.StatusCode < 200 || httpResp.StatusCode >= 300 {
		detail, _ := io.ReadAll(io.LimitReader(httpResp.Body, maxErrorDetail))
		return "", fmt.Errorf("%s: %s", httpResp.Status, strings.TrimSpace(string(detail)))
	}

	var decoded chatResponse
	if err := json.NewDecoder(httpResp.Body).Decode(&decoded); err != nil {
		return "", fmt.Errorf("decode response: %w", err)
	}
	if len(decoded.Choices) == 0 {
		return "", errors.New("model returned no choices")
	}
	return decoded.Choices[0].Message.Content, nil
}

// readFrame decodes a 4-byte little-endian length prefix followed by JSON.
func readFrame(conn net.Conn, dst any) error {
	header := make([]byte, 4)
	if _, err := io.ReadFull(conn, header); err != nil {
		return err
	}

	size := binary.LittleEndian.Uint32(header)
	if size == 0 || size > maxFrameSize {
		return fmt.Errorf("invalid frame size %d", size)
	}

	payload := make([]byte, size)
	if _, err := io.ReadFull(conn, payload); err != nil {
		return err
	}
	return json.Unmarshal(payload, dst)
}

// writeFrame encodes src as JSON behind the same 4-byte length prefix.
func writeFrame(conn net.Conn, src any) error {
	payload, err := json.Marshal(src)
	if err != nil {
		return err
	}

	frame := make([]byte, 4+len(payload))
	binary.LittleEndian.PutUint32(frame, uint32(len(payload)))
	copy(frame[4:], payload)

	_, err = conn.Write(frame)
	return err
}
