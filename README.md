# CALISTRA
Program that combines the capabilities of applications for maintaining to-do lists, calendars and task trackers

## Functionality:

1. Creating, editing and removing single task.
2. Ability to split a task into subtasks.
3. Task can have start time, deadline, reminders, description and other information
4. Mechanism of related tasks(blockers and controllers). One task can block the execution of another, or manage task status.
5. The placement of tasks in the queue. Еhis mechanism allows locate tasks in one common place.
6. Periodic plans mechanism. You can schedule a task for a specific time, and the program will automatically create the task for that time.
7. Working in command. You can create accounts. Every task has an author and users who responsible to do this task.
8. Notifications system. Editing, deleting a task, or approaching a due date will not be left without notifying the users of the task


## Architecture
The program consists of two logical parts - a console application and a library, which is reflected in the directory hierarchy.
The library concentrates the basic logic of work with the program entities - users, tasks and plans. You can use it separately from the console interface or by using the library modules in your own program. You can just import it!
A console application is a program running in the command window. It performs validation and authentification of user data, checking the correctness of the information entered. After that it uses calls from the library to process the data, and displays the results. Сommand-line arguments are used for all program operations.


## Installing
For installing application perform next operations:

#### Clone repository:
```bash
$ git clone https://IgorTurcevich@bitbucket.org/IgorTurcevich/calistra.git
```

#### Install console application:
```bash
$ cd calistra
$ python3 -m pip install . --user
```

#### Install program library
```bash
$ cd lib
$ python3 -m pip install . --user
``` 

## How to use
First of all, check help message:
```bash
$ calistra --help
```

It will show information about commands and their usage. You need to remeber, that this help message show info only for current program command level. For show commands info use:
```bash
$ calistra <target> <action> --help
```

For example:
```bash
$ calistra task --help
$ calistra task add --help
```

### First steps

#### Configuration

You can determine where the data is stored in the computer. The default is the home directory:
```bash
$ calistra config set settings --path=/home
```

You can also edit logger configuration:
1. Level of configuration:

    ```bash
    $ calistra config set logger --level=WARNING
    ```  
    
2. File for logs:

    ```bash
    $ calistra config set logger --file=/home/user/Desctop/my_program_logs.log
    ```  
     
3. Enable or disable logger:

    ```bash
    $ calistra config set logger --enabled=True
    ```
    ```bash
    $ calistra config set logger --enabled=False
    ```


#### User account

After that you can create account, which you will use in the process of working in the program

```bash
$ calistra user add <nick> <password>
```

Next step you need to login. To do this, enter the data used to create the user:

```bash
$ calistra user login <nick> <password>
```

Congratulations! Now you can take advantage of the full functionality of the program.

### Working with tasks
Let's look at the basic functionality of the program, its main features and commands for executing:

#### Creating a simple task:
```bash
$ calistra task add 'First task'
```

After that you will see message, for example:
"Task "First task" added. It's key - 0e723a3aada16c7e"

Key is set of numbers and letters. It is using for access, deleting and editing task. It's not neccessary to remember this key. If you want to remind this key you can find task by name.
If an argument consists of several words, it must be quoted !!!

#### Search task:
```bash
$ calistra task find 'First task'
```

Result will be next:
Search:
|	Result for "First task":
|	|	1) Name: "First task", key: 0e723a3aada16c7e, queue: 26da9808 updated: 24.08.2018.03:20:12, status: opened, deadline: None

#### Editing task:
```bash
$ calistra task set <task_key> <task_attrs>
```

For example:

```bash
$ calistra task set 0e723a3aada16c7e --description='very important task' --start=22.08.2018.9:00
```

Program message:
"Task with key "0e723a3aada16c7e" edited"

For more information:
```bash
$ calistra task set --help
```

#### Creating sub task:
Organizing task using sub task can help decompose problem into smaller part. 
For this you need to have created task. For example we use task created above:
```bash
$ calistra task add 'Sub task' --parent=0e723a3aada16c7e
```

#### Solving task:
The status parameter is responsible for the status of the task:
```bash
$ calistra task set <task_key> --status=solved
```

#### Removing task:

```bash
$ calistra task del <task_key>
```

If task has subtasks program inform you about this. For deleting task with subtasks use optional argument -r:

```bash
$ calistra task del <task_key> -r
```


### Working with queues
А queue is a container for tasks. Сonsider the basic functionality of queues:

#### Creating a queue:
```bash
$ calistra queue add 'My queue'
```

#### Adding task to the queue:
```bash
$ calistra task set <task_key> --queue=<queue_key>
```

#### View queue content:

```bash
$ calistra queue show <queue_key>
```

#### Delete queue:
```bash
$ calistra queue del <queue_key>
```
Note: user argument -r for delete queue with content


### Reminder mechanism
Calistra allows you to create a reminder mechanism for the imminent occurrence of the task:

```bash
$ calistra task set <task_key> --reminder=every_day:19.00
```
It's mean that while task is open program every day will be notify you to complete the task. 
For example, "REMINDER: Task "2 plan"(c8560d3e0ea9) deadline tomorrow at 02:18:00"

### Periodic plans
You can create a periodic plan, which according to the parameters will create a task that you will need to perform. All tasks created by the plan is placed in the queue "default'

```bash
$ calistra plan add <plan_name> <period> <activation_time> <--reminder>
```

For example:

```bash
$ calistra plan add 'Brush teeth' 'daily' '22.08.2018.18:00'
```

For deleting plan use:

```bash
$ calistra plan del <plan_key>
```


We have reviewed the basic principles of the application. For the rest of information see program help messages...

