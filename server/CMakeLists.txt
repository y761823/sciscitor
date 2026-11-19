# Go toolchain: required on PATH. A Go provided by mise's global configuration
# is accepted as a fallback, but the project itself does not depend on mise.
find_program(GO_EXECUTABLE go)
if(GO_EXECUTABLE)
    set(GO_CMD "${GO_EXECUTABLE}")
else()
    # A Go coming from mise's global config is still accepted, but only if mise
    # can actually resolve one: verify it here so a missing toolchain fails at
    # configure time instead of during the build.
    set(_mise_go_available FALSE)
    find_program(MISE_EXECUTABLE mise)
    if(MISE_EXECUTABLE)
        execute_process(
            COMMAND "${MISE_EXECUTABLE}" exec -- go version
            RESULT_VARIABLE _mise_go_status
            OUTPUT_QUIET
            ERROR_QUIET)
        if(_mise_go_status EQUAL 0)
            set(_mise_go_available TRUE)
        endif()
    endif()

    if(NOT _mise_go_available)
        message(FATAL_ERROR
            "Go 1.26+ was not found on PATH.\n"
            "Install it with 'winget install GoLang.Go' or the official installer.\n"
            "See docs/environment.md for details.")
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

# Installed next to the client executable so the client finds it in the same
# directory.
install(PROGRAMS "${SERVER_EXE}" DESTINATION ${CMAKE_INSTALL_BINDIR})
