cmake_minimum_required(VERSION 3.27)

project(Sciscitor VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Guard against an unedited CMakeUserPresets.json.example: fail with a clear
# instruction instead of a vague "Could not find Qt6" from find_package().
foreach(_var CMAKE_PREFIX_PATH CMAKE_TOOLCHAIN_FILE)
    if("${${_var}}" MATCHES "<")
        message(FATAL_ERROR
            "${_var} still contains a placeholder.\n"
            "Edit CMakeUserPresets.json and fill in the real path for this machine.\n"
            "See docs/environment.md for details.")
    endif()
endforeach()

include(GNUInstallDirs)

add_subdirectory(client)
add_subdirectory(server)
