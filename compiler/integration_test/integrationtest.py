import unittest
import subprocess
import os
import shutil
import inspect


class IntegrationTest:

    def __init__(self):
        self.python = "python3.8"
        self.bipage_path = "../bipage.py"
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        self.test_name = os.path.splitext(os.path.basename(module.__file__))[0]
        self.tempdir = f'temp_{self.test_name}'
        self.clean_temp_dir()

    def clean_temp_dir(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)
        os.mkdir(self.tempdir)

    def write_bipage_file(self, content):
        with open(f'temp_{self.test_name}/{self.test_name}.bp', 'w+') as f:
            f.write(content)

    def write_cmake_file(self):
        with open(f'temp_{self.test_name}/CMakeLists.txt', 'w+') as f:
            f.write(f'''
        cmake_minimum_required(VERSION 3.4)

        # set the project name
        project(integration_test)
        
        # Set the include path
        include_directories(../../../library/c++)

        # add the executable
        add_executable({self.test_name} {self.test_name}.cpp)

        # specify the C++ standard
        set(CMAKE_CXX_STANDARD 11)
        set(CMAKE_CXX_STANDARD_REQUIRED True)
        set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} -std=c++11")''')

    def write_test_cpp_file(self, content):
        with open(f'temp_{self.test_name}/{self.test_name}.cpp', 'w+') as f:
            f.write(content)

    def run_bipage(self, args=None):
        to_execute = [self.python, self.bipage_path, "-i", f"temp_{self.test_name}/{self.test_name}.bp", '-o',
                      f'temp_{self.test_name}']
        if args:
            to_execute.extend(args)
        subprocess.call(to_execute)


    def run_cmake(self):
        subprocess.call(["cmake", "./"], cwd=f'temp_{self.test_name}/')
        subprocess.call(["cmake", "--build", "."], cwd=f'temp_{self.test_name}/')

    def run_test(self, args = None):
        result = subprocess.run([f"temp_{self.test_name}/{self.test_name}", 'simple'], stdout=subprocess.PIPE)
        return (result.returncode, result.stdout.decode('utf-8'))

    def run_all(self, bipageargs=None):
        self.run_bipage(bipageargs)
        self.run_cmake()
        return self.run_test()