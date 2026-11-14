package main

import (
	"flag"
	"fmt"
	"os"
)

// version is injected at build time via
// -ldflags "-X main.version=<project version>"
var version = "dev"

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

	fmt.Printf("sciscitor-server %s listening on %s\n", version, *pipeName)

	// TODO: listen on the named pipe and serve requests.
}
