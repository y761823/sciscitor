# Go toolchain: prefer PATH, fall back to mise (go version is pinned in mise.toml)
find_program(GO_EXECUTABLE go)
if(GO_EXECUTABLE)
    set(GO_CMD "${GO_EXECUTABLE}")
else()
    find_program(MISE_EXECUTABLE mise)
    if(NOT MISE_EXECUTABLE)
        message(FATAL_ERROR
            "Neither 'go' nor 'mise' was found. Run 'mise install' and make sure mise is on PATH.")
    endif()
    set(GO_CMD "${MISE_EXECUTABLE}" exec -- go)
endif()

set(SERVER_OUTPUT_DIR "${CMAKE_BINARY_DIR}/bin")
set(SERVER_EXE "${SERVER_OUTPUT_DIR}/sciscitor-server${CMAKE_EXECUTABLE_SUFFIX}")

file(GLOB_RECURSE SERVER_SOURCES CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.go"
)
list(APPEND SERVER_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/go.mod")

add_custom_command(
    OUTPUT "${SERVER_EXE}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${SERVER_OUTPUT_DIR}"
    COMMAND ${CMAKE_COMMAND} -E env CGO_ENABLED=0
            ${GO_CMD} build
            -trimpath
            "-ldflags=-s -w -X main.version=${PROJECT_VERSION}"
            -o "${SERVER_EXE}"
            .
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS ${SERVER_SOURCES}
    COMMENT "Building sciscitor-server (version ${PROJECT_VERSION})"
    VERBATIM
)

add_custom_target(sciscitor_server ALL DEPENDS "${SERVER_EXE}")
