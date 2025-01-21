from types import MethodType
from typing import TypeVar, Any, Protocol, Callable, TypedDict, NotRequired, Any, Type

from .. import logger


# class CsLoaderComponent:
#     def __init__(self, *args, loadable_components: dict):
#         self._loadable_components = loadable_components
#         self._loaded_components = set()
#         if args:
#             self.load_components(*args)

#     def load_components(self, *args) -> None:
#         if "ALL" in args:
#             args = set(self._loadable_components) - {"_loader_init_remove"}
#         for task in args:
#             if task in self._loaded_components:
#                 fn_log(f"{task} has already been loaded so skip")
#                 continue
#             if task in set(self._loadable_components) - {"_loader_init_remove"}:
#                 for key, value in self._loadable_components[task].items():
#                     match key:
#                         case "__init__component":
#                             MethodType(value, self)()
#                         case "__remove__component":
#                             pass
#                         case _:
#                             setattr(
#                                 self,
#                                 key,
#                                 MethodType(value, self) if callable(value) else value,
#                             )
#             else:
#                 raise AttributeError(
#                     f"'{task}' is not a valid task for {self.__class__.__name__}, try {list(self._loadable_components.keys())} or 'ALL' "
#                 )
#             if self._loadable_components.get("_loader_init_remove"):
#                 MethodType(
#                     self._loadable_components["_loader_init_remove"]["__init__loader"],
#                     self,
#                 )(task)
#             self._loaded_components.add(task)
#             fn_log(f"{task} loaded successfully")
#         return None

#     def remove_components(self, *args) -> None:
#         if "ALL" in args:
#             args = set(self._loadable_components) - {"_loader_init_remove"}
#         for task in args:
#             if task in self._loaded_components:
#                 for key, value in self._loadable_components[task].items():
#                     match key:
#                         case "__init__component":
#                             pass
#                         case "__remove__component":
#                             MethodType(value, self)()
#                         case _:
#                             if hasattr(self, key):
#                                 delattr(self, key)
#                 if self._loadable_components.get("_loader_init_remove"):
#                     MethodType(
#                         self._loadable_components["_loader_init_remove"][
#                             "__remove__loader"
#                         ],
#                         self,
#                     )(task)
#                 self._loaded_components.remove(task)
#                 fn_log(f"{task} removed successfully")
#             else:
#                 raise AttributeError(
#                     f"'{task}' components is not loaded or component {task} doesn't exists"
#                 )
#         return None


# class CsMultiSeed:
#     def __init__(self, index):
#         self._index = index

#     def _close_instance(self):
#         if self._helper_driver:
#             self._helper_driver.close()
#         self.close()  # depends on the instance
#         self.quit()


# class CsMultiManager_Protocol(Protocol):
#     _instances: dict[int, Callable]
#     _subclass: Callable
#     _sources: dict
#     _args: set[Any]
#     _kwargs: dict[str, Any]


# class CsMultiManager(CsMultiManager_Protocol):
#     def __init__(self, *args, threads, subclass, **kwargs) -> None:
#         for key, value in {
#             "instances": {},
#             "sources": {},
#             "threads": 0,
#             "subclass": subclass,
#             "args": set(args),
#             "kwargs": kwargs,
#         }.items():
#             setattr(self, "_" + key, value)
#         # init instances
#         self.threads = threads

#     def _init_instances(self) -> None:
#         def _init_instance(*args, index: int, **kwargs):
#             if index in self._instances:
#                 fn_log(f"{index} instance already exists so pass")
#                 return
#             fn_log(f"start initializing {index} instance")
#             self._instances.update(
#                 {index: self._subclass(*args, index=index, **kwargs)}
#             )

#         multithreading(
#             call_def=_init_instance,
#             source=None,
#             threads=self._threads,
#             args=tuple(self._args),
#             kwargs=self._kwargs,
#         )

#     def _call_instances(self, handler: str, threads: Optional[int] = None) -> Callable:
#         if threads is None:
#             threads = self._threads
#         if threads <= 0:
#             raise ValueError("threads must be positive integer( >0 )")

#         def _def_wrapper(*args, source: Any = None, threads: int = threads, **kwargs):
#             match threads:
#                 case _ if threads <= 0:
#                     raise ValueError("threads must be positive integer( >0 )")
#                 case _ if threads > self._threads:
#                     self.threads = threads
#                 case _:
#                     pass
#             # split source into self._sources
#             if isinstance(source, (list, tuple, dict)):
#                 self._sources.clear()
#                 multithreading(
#                     call_def=lambda source, index: self._sources.update(
#                         {index: source}
#                     ),
#                     source=source,
#                     threads=threads,
#                 )
#             # execute instances def
#             multithreading(
#                 call_def=lambda *args, index, **kwargs: getattr(
#                     self._instances[index], handler
#                 )(*args, **kwargs),
#                 source=source,
#                 threads=threads,
#                 args=args,
#                 kwargs=kwargs,
#             )

#         return _def_wrapper

#     @property  # Getter
#     def threads(self) -> int:
#         return self._threads

#     @threads.setter  # Setter
#     def threads(self, threads: int) -> None:
#         if not isinstance(threads, int) or threads < 0:
#             raise TypeError(f"threads must > 0")
#         match threads:
#             case self._threads:
#                 fn_log(f"current threads {threads} unchanged")
#             case _ if threads > self._threads:
#                 self._threads = threads
#                 self._init_instances()
#             case _ if threads < self._threads:
#                 for i in range(threads, self._threads):
#                     self._instances[i]._close_instance()
#                     self._instances.pop(i)
#                 self._threads = threads


# class CsMultiLoaderEntry(CsMultiManager_Protocol):
#     def __init__(self):
#         if self.threads == 0:
#             self.threads = 1
#         self._instances_loadable_components = self._instances[0]._loadable_components
#         for task in self._args:
#             for handler in self._instances_loadable_components[task]:
#                 if not task.startswith("_"):
#                     setattr(self, handler, self._call_instances(handler=handler))

#     def load_instances_components(self, *args, threads: Optional[int] = None) -> None:
#         if "ALL" in args:
#             args = set(self._instances_loadable_components)
#         for task in args:
#             if task in self._args:
#                 fn_log(f"{task} has already been loaded so skip")
#                 continue
#             if task in self._instances_loadable_components:
#                 # load component to instances
#                 self._call_instances(handler="load_components")(task)
#                 # set handler entrance for multi_manager
#                 for handler in self._instances_loadable_components[task]:
#                     if not task.startswith("_"):
#                         setattr(
#                             self,
#                             handler,
#                             self._call_instances(handler=handler, threads=threads),
#                         )
#             else:
#                 raise AttributeError(
#                     f"'{task}' is not a valid task for {self.__class__.__name__}, try {set(self._instances_loadable_components)} or 'ALL' "
#                 )
#             self._args.add(task)
#             fn_log(f"{task} entry loaded successfully")

#     def remove_instances_components(self, *args) -> None:
#         if "ALL" in args:
#             args = set(self._args)
#         for task in args:
#             if task in self._args:
#                 # remove component for instances
#                 self._call_instances("remove_components")(task)
#                 for key in self._instances_loadable_components[task]:
#                     if "handler" in key and hasattr(self, key):
#                         delattr(self, key)
#                 self._args.remove(task)
#                 fn_log(f"{task} entry removed successfully")
#             else:
#                 raise AttributeError(
#                     f"'{task}' components is not loaded or component {task} doesn't exists"
#                 )

#     def crawling_main(
#         self,
#         task,
#         source: Optional[list] = None,
#         threads: Optional[int] = None,
#         **kwargs,
#     ):
#         if source:
#             fn_log(f"Start {task}, total source count : {len(source)}")

#         # load task
#         if task not in self._args:
#             self.load_instances_components(task, threads=threads)

#         # execute
#         getattr(self, task + "_handler")(source=source, **kwargs)


# class my_loader:
#     def load_components(self, obj: object, **kwargs) -> None:
#         for key, value in kwargs.items():
#             match key:
#                 case "__init__component":
#                     MethodType(value, obj)()
#                 case "__remove__component":
#                     pass
#                 case _:
#                     setattr(
#                         obj, key, MethodType(value, self) if callable(value) else value
#                     )
#             fn_log(f"{key} loaded successfully")

#     def remove_components(self, obj: object, **kwargs) -> None:
#         for key, value in kwargs.items():
#             match key:
#                 case "__init__component":
#                     pass
#                 case "__remove__component":
#                     MethodType(value, self)()
#                 case _:
#                     if hasattr(obj, key):
#                         delattr(obj, key)
#             fn_log(f"{key} removed successfully")


# class config_dict_type(TypedDict):
#     default_args: NotRequired[list[Any]]
#     all_args: NotRequired[bool]
#     default_kwargs: NotRequired[dict[str, Any]]
#     all_kwargs: NotRequired[bool]


# def cs_factory(dic_cs: dict[Type, Optional[config_dict_type]]):
#     bases = tuple(dic_cs.keys())
#     slots = {
#         slot
#         for base in bases
#         if hasattr(base, "__slots__")
#         for slot in getattr(base, "__slots__")
#     }

#     # Define the dynamic class with type
#     def init(self, *args, **kwargs):
#         # config = {default_args': [],'all_args': bool,'default_kwargs': {},'all'd_kwargs': bool}
#         for Cs, config in dic_cs.items():
#             if config is None:
#                 continue
#             _args = config.get("default_args", []) + (
#                 [*args] if config.get("all_args", False) else []
#             )
#             _kwargs = config.get("default_kwargs", {}) | (
#                 kwargs
#                 if config.get("all_kwargs", False)
#                 else {
#                     key: kwargs.get(key, value)
#                     for key, value in config.get("default_kwargs", {}).items()
#                 }
#             )
#             # print(f"{Cs.__name__} : {config = }")
#             # print(f"{Cs.__name__} : {_args = }")
#             # print(f"{Cs.__name__} : {_kwargs = }")
#             Cs.__init__(self, *_args, **_kwargs)

#     # Create the class with type
#     return type("_Cs", bases, {"__slots__": slots, "__init__": init})

# Define a generic type T that is bound to object
T = TypeVar("T", bound=object)


def compose(obj: T, funcs: dict[str, Any], by_class: bool = False) -> int:
    new_obj: type[T] | T = obj.__class__ if by_class else obj
    for key, value in funcs.items():
        match key:
            case "__compose_init__":
                MethodType(value, new_obj)()
            case "__decompose__":
                # Placeholder for future implementation
                pass
            case _:
                setattr(
                    new_obj,
                    key,
                    MethodType(value, new_obj) if callable(value) else value,
                )
        logger.info(f"{key} loaded successfully")
    return 0


def decompose(obj: T, funcs: dict[str, Any], by_class: bool = False) -> object:
    new_obj: type[T] | T = obj.__class__ if by_class else obj
    for key, value in funcs.items():
        match key:
            case "__compose_init__":
                # Placeholder for future implementation
                pass
            case "__decompose__":
                MethodType(value, new_obj)()
            case _:
                if hasattr(new_obj, key):
                    delattr(new_obj, key)
    logger.info(f"{key} removed successfully")

    return 0
