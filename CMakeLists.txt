cmake_minimum_required (VERSION 2.6)
project(utils)

find_package(Threads)
#find_package(Boost COMPONENTS program_options)
#include_directories(${Boost_INCLUDE_DIRS})

add_executable(downtracker downtracker.c)
target_link_libraries(downtracker ${CMAKE_THREAD_LIBS_INIT})

add_executable(portforward portforward.c)

install(TARGETS downtracker portforward RUNTIME DESTINATION bin )