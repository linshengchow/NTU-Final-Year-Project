from setuptools import find_packages, setup

package_name = 'multi_floor_manager'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='linsheng',
    maintainer_email='linshengchow@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'multi_floor_manager = multi_floor_manager.lift_script:main',
            'execution_controller = multi_floor_manager.execution_controller:main',
        ],
    },
)
