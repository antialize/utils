cmake_minimum_required (VERSION 2.6)

project(antializeutils)

set(CPACK_PACKAGE_NAME "antialize-utils")
set(CPACK_PACKAGE_VERSION "0.1")
set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE amd64)
set(CPACK_PACKAGE_CONTACT antialize@gmail.com)
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Antialize's utilities")
set(CPACK_PACKAGE_DESCRIPTION "Antialize's utilities")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "uuid")
set(CPACK_GENERATOR "DEB")

INCLUDE(CPack)
find_package(Threads)
#find_package(Boost COMPONENTS program_options)
#include_directories(${Boost_INCLUDE_DIRS})

add_executable(downtracker downtracker.c)
target_link_libraries(downtracker ${CMAKE_THREAD_LIBS_INIT})

add_executable(portforward portforward.c)

add_executable(atsort atsort.cc)

install(TARGETS downtracker portforward atsort RUNTIME DESTINATION bin )

install(PROGRAMS bookplayer.sh DESTINATION bin RENAME bookplayer)

