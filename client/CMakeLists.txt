find_package(Qt6 6.12 REQUIRED COMPONENTS Quick QuickControls2)

qt_standard_project_setup(REQUIRES 6.12)

qt_add_executable(appSciscitorClient
    main.cpp
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
    PRIVATE Qt6::Quick Qt6::QuickControls2
)

install(TARGETS appSciscitorClient
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
