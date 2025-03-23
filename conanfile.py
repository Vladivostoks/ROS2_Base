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
        self.run(f"source venv/bin/activate\
        && mkdir -p src \
        && export PYTHONPATH=\"{self.source_folder}/venv/lib/python3.13/site-packages:$PYTHONPATH\"\
        && vcs import src < ros2_base.repos \
        && colcon build \
            --symlink-install \
            --merge-install \
            --event-handlers console_cohesion+ console_package_list+ \
            --packages-up-to rclcpp std_msgs ros2cli launch\
            --cmake-args \
            --no-warn-unused-cli \
            -DBUILD_TESTING=OFF \
            -DINSTALL_EXAMPLES=ON \
            -DCMAKE_PREFIX_PATH={self.generators_folder}\
            -DAsio_INCLUDE_DIR={self.dependencies["asio"].package_folder}/include\
            -Dtinyxml2_DIR={self.dependencies["tinyxml2"].package_folder}\
            ",
            cwd=self.source_folder)

    def package(self):
        pass

    def package_info(self):
        pass

