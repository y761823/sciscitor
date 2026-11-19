find_package(Qt6 6.12 REQUIRED COMPONENTS Quick QuickControls2 Network)

qt_standard_project_setup(REQUIRES 6.12)

qt_add_executable(appSciscitorClient
    main.cpp
    backend.cpp
    backend.h
)

qt_add_qml_module(appSciscitorClient
    URI SciscitorClient
    QML_FILES
        Main.qml
)

set_target_properties(appSciscitorClient PROPERTIES
    WIN32_EXECUTABLE TRUE
)

target_link_libraries(appSciscitorClient
    PRIVATE Qt6::Quick Qt6::QuickControls2 Qt6::Network
)

install(TARGETS appSciscitorClient
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# Runs windeployqt at install time, the same way Qt Creator's Deploy step does.
# The QML variant also deploys the QML imports used by Main.qml; the plain
# qt_generate_deploy_app_script leaves them out and the app fails to start.
qt_generate_deploy_qml_app_script(
    TARGET appSciscitorClient
    OUTPUT_SCRIPT deploy_script
    NO_UNSUPPORTED_PLATFORM_ERROR
)
install(SCRIPT ${deploy_script})
