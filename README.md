# rga-drivers
Driver scripts for the SRS RGA used in the Stanford liquid xenon lab.

## Overview
This package contains the custom drivers we use with the SRS RGA software, in addition to some functions used to do real-time analysis of the RGA data as it comes in. The instructions below detail how a frequently-repeated measurement can be coded up as a task which we can easily call from the `srsinst.rga` menu bar.

## Making a Task
The basic steps for making a new task are as follows:
#### 1. Define the class in `src/lxedrivers/tasks.py`
The class for the new task should inherit either from the existing `srsgui.Task` class, or from one of its child classes defined in the `srsinst.rga.tasks` module. For example, the `IsotopeAnalysis` class inherits from `srsinst.rga.tasks.analogscantask.AnalogScanTask` class, because it reuses a lot of the basic functionality.
#### 2. Write `setup`, `test`, and `cleanup` methods
To avoid overriding essential methods from the parent classes, we should only be touching these three methods. In the `IsotopeAnalysis` case, the majority of additions to the code occur in the `test` method that runs the main scan acquisition loop. There, I added some code to write the data to a file and compute and print the real-time isotopic abundance measurement. To avoid cluttering this module, which should really only have task classes, each with the three aforementioned methods, I've put additional functions into either the `utils` or `analysis` module. The `utils` module contains basic utilities for saving, loading, etc. while the `analysis` module contains the physics analysis functions.
#### 3. Build the `lxedrivers` package.
In order for the `srsinst.rga` software to identify the new tasks, they need to be easily importable from other directories. To achieve this, I've added a simple `pyproject.toml` file that will allow us to install the `lxedrivers` package in the same virtual environment from which the `srsinst.rga` software is called. Building the package is done as follows:
```cmd
cd C:\Users\lxere\Software
srsint-rga-env\Scripts\activate
cd rga-drivers
pip install .
```
#### 4. Add the new task to the `lxedrivers.taskconfig` file
For the sake of simplicity, we can keep all our frequent tasks in this single `.taskconfig` file. To add a task, we give the task name, the importable module containing the task, and the task class, in the following format:
```
task: New task name,       lxedrivers.tasks,				  NewTaskClass
```
Any time the new class is updated, we have to rebuild the python package and reload the `.taskconfig` file from within the `srsinsts.rga` software. Following this, the new task should be available under the Tasks menu bar item.

## Other Documentation
For more information on writing tasks, look to the [`srsinst.rga` documentation](https://thinksrs.github.io/srsinst.rga/index.html) and the [`srsgui` documentation](https://thinksrs.github.io/srsgui/index.html).
