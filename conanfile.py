from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps


class Recipe(ConanFile):
    name = "ros2_base"
    version = "1.0.0"
    package_type = "build-scripts"

    # Optional metadata
    license = "Apache 2.0"
    url = "https://github.com/Vladivostoks/ROS2_Base"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    tool_requires = "cmake/3.31.6"
    requires = [
        "asio/1.28.2",
        "tinyxml2/10.0.0",
    ]

    options = {
        "dds_type": ["fastdds"], 
    }
    default_options = {
        "dds_type": "fastdds",
    }

    exports = "ros2_base.repos"

    def system_requirements(self):
        # 创建虚拟环境
        self.run("python3 -m venv venv")
        # 安装 Python 依赖
        self.run("venv/bin/pip install -r requirements.txt")

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        build_type = self.settings.get_safe("build_type", default="Release")

        self.run(f"source venv/bin/activate\
        && mkdir -p src \
        && export PYTHONPATH=\"{self.source_folder}/venv/lib/python3.13/site-packages:$PYTHONPATH\"\
        && vcs import src < ros2_base.repos \
        && cp ros-patch/py13.patch src/ros2/pybind11_vendor\
        && cp ros-patch/pybind11_vendor.patch src/ros2/pybind11_vendor\
        && cd src/ros2/pybind11_vendor \
            git restore || git apply pybind11_vendor.patch\
        && cd -\
        && colcon build \
            --symlink-install \
            --merge-install \
            --event-handlers console_cohesion+ console_package_list+ \
            --packages-skip my-test-package \
            --cmake-args \
            --no-warn-unused-cli \
            -DINSTALL_EXAMPLES=ON \
            -DCMAKE_PREFIX_PATH={self.generators_folder}\
            -DCMAKE_BUILD_TYPE=\"{build_type}\"\
            -DAsio_INCLUDE_DIR={self.dependencies['asio'].package_folder}/include\
            -Dtinyxml2_DIR={self.dependencies['tinyxml2'].package_folder}\
            ",
            cwd=self.source_folder)

    def package(self):
        self.run(f"cp -rf build {self.package_folder}", cwd=self.source_folder)
        self.run(f"cp -rf install {self.package_folder}", cwd=self.source_folder)

    def package_info(self):
        pass

