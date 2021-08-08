# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Dict


def create_train_ann_config(reader_json_conf_directory_in: str, write_erg_path: str,
                            process_cnt: int, dump_size: int, keep_dump: bool, /) -> Dict:
    return {
        "WorkableConf": {
            "ReaderJsonConfig": {
                "ReWrInterface": "ReaderJson",
                "WorkInterface": "WorkerCreateNetStructure",
                "ArgsReWr": {
                    "directory_in": reader_json_conf_directory_in
                },
                "ArgsWork": {
                    "container_proto": "NeuralNetStructureTrainCon"
                }
            },
            "AnnTrainNet": {
                "ReWrInterface": "SyncQueue",
                "WorkInterface": "WorkerTrainNet",
                "ArgsReWr": {
                    "puffer_size": "10",
                    "container_proto": "NeuralNetStructureTrainCon"
                },
                "ArgsWork": {}
            },
            "WriterErg": {
                "ReWrInterface": "WriterNetTrainTest",
                "WorkInterface": "EndWork",
                "ArgsReWr": {
                    "working_path": write_erg_path,
                    "dump_size": 'F' if dump_size <= 0 else str(dump_size),
                    "keep_dump": 'T' if keep_dump else 'F'
                },
                "ArgsWork": {}
            }
        },
        "WorkerConf": {
            "TrainStructure": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "ReaderJsonConfig",
                "WorkableOut": "AnnTrainNet",
                "WorkerIn": ["Start"],
                "WorkerOut": ["TrainRun"],
                "WorkInTypes": ["JsonDictCon"],
                "WorkOutTypes": ["NeuralNetStructureTrainCon"]
            },
            "TrainRun": {
                "ProcessCnt": 1 if process_cnt <= 0 else process_cnt,
                "GroupCnt": 1,
                "WorkableIn": "AnnTrainNet",
                "WorkableOut": "WriterErg",
                "WorkerIn": ["TrainStructure"],
                "WorkerOut": ["End"],
                "WorkInTypes": ["NeuralNetStructureTrainCon"],
                "WorkOutTypes": ["TestNNStatsCon", "TrainNNStatsCon", "NeuralNetSaveCon"]
            }
        }
    }


def create_check_train_ann_config(reader_json_conf_directory_in: str, /) -> Dict:
    return {
        "WorkableConf": {
            "ReaderJsonConfig": {
                "ReWrInterface": "ReaderJson",
                "WorkInterface": "WorkerCreateNetStructure",
                "ArgsReWr": {
                    "directory_in": reader_json_conf_directory_in
                },
                "ArgsWork": {
                    "container_proto": "NeuralNetStructureTrainCon"
                }
            },
            "AnnTrainNet": {
                "ReWrInterface": "SyncQueue",
                "WorkInterface": "WorkerCheckNet",
                "ArgsReWr": {
                    "puffer_size": "10",
                    "container_proto": "NeuralNetStructureTrainCon"
                },
                "ArgsWork": {
                    "container_proto": "NeuralNetStructureTrainCon"
                }
            },
            "OutputSink": {
                "ReWrInterface": "NoOutputSink",
                "WorkInterface": "EndWork",
                "ArgsReWr": {
                    "container_proto": "EmptyContainer"
                },
                "ArgsWork": {}
            }
        },
        "WorkerConf": {
            "TrainStructure": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "ReaderJsonConfig",
                "WorkableOut": "AnnTrainNet",
                "WorkerIn": ["Start"],
                "WorkerOut": ["TrainRun"],
                "WorkInTypes": ["JsonDictCon"],
                "WorkOutTypes": ["NeuralNetStructureTrainCon"]
            },
            "TrainRun": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "AnnTrainNet",
                "WorkableOut": "OutputSink",
                "WorkerIn": ["TrainStructure"],
                "WorkerOut": ["End"],
                "WorkInTypes": ["NeuralNetStructureTrainCon"],
                "WorkOutTypes": ["EmptyContainer"]
            }
        }
    }


def create_test_ann_config(reader_json_conf_directory_in: str, write_erg_path: str, /) -> Dict:
    return {
        "WorkableConf": {
            "ReaderJsonConfig": {
                "ReWrInterface": "ReaderJson",
                "WorkInterface": "WorkerCreateNetStructure",
                "ArgsReWr": {
                    "directory_in": reader_json_conf_directory_in
                },
                "ArgsWork": {
                    "container_proto": "NeuralNetStructureTestCon"
                }
            },
            "AnnTestNet": {
                "ReWrInterface": "SyncQueue",
                "WorkInterface": "WorkerTestNet",
                "ArgsReWr": {
                    "puffer_size": "10",
                    "container_proto": "NeuralNetStructureTestCon"
                },
                "ArgsWork": {}
            },
            "WriterErg": {
                "ReWrInterface": "WriterNetTrainTest",
                "WorkInterface": "EndWork",
                "ArgsReWr": {
                    "working_path": write_erg_path,
                    "dump_size": 'F',
                    "keep_dump": 'F'
                },
                "ArgsWork": {}
            }
        },
        "WorkerConf": {
            "TestStructure": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "ReaderJsonConfig",
                "WorkableOut": "AnnTestNet",
                "WorkerIn": ["Start"],
                "WorkerOut": ["TestRun"],
                "WorkInTypes": ["JsonDictCon"],
                "WorkOutTypes": ["NeuralNetStructureTestCon"]
            },
            "TestRun": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "AnnTestNet",
                "WorkableOut": "WriterErg",
                "WorkerIn": ["TestStructure"],
                "WorkerOut": ["End"],
                "WorkInTypes": ["NeuralNetStructureTestCon"],
                "WorkOutTypes": ["TestNNStatsCon"]
            }
        }
    }


def create_check_test_ann_config(reader_json_conf_directory_in: str, /) -> Dict:
    return {
        "WorkableConf": {
            "ReaderJsonConfig": {
                "ReWrInterface": "ReaderJson",
                "WorkInterface": "WorkerCreateNetStructure",
                "ArgsReWr": {
                    "directory_in": reader_json_conf_directory_in
                },
                "ArgsWork": {
                    "container_proto": "NeuralNetStructureTestCon"
                }
            },
            "AnnTestNet": {
                "ReWrInterface": "SyncQueue",
                "WorkInterface": "WorkerCheckNet",
                "ArgsReWr": {
                    "puffer_size": "10",
                    "container_proto": "NeuralNetStructureTestCon"
                },
                "ArgsWork": {
                    "container_proto": "NeuralNetStructureTestCon"
                }
            },
            "OutputSink": {
                "ReWrInterface": "NoOutputSink",
                "WorkInterface": "EndWork",
                "ArgsReWr": {
                    "container_proto": "EmptyContainer"
                },
                "ArgsWork": {}
            }
        },
        "WorkerConf": {
            "TestStructure": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "ReaderJsonConfig",
                "WorkableOut": "AnnTestNet",
                "WorkerIn": ["Start"],
                "WorkerOut": ["TestRun"],
                "WorkInTypes": ["JsonDictCon"],
                "WorkOutTypes": ["NeuralNetStructureTestCon"]
            },
            "TestRun": {
                "ProcessCnt": 1,
                "GroupCnt": 1,
                "WorkableIn": "AnnTestNet",
                "WorkableOut": "OutputSink",
                "WorkerIn": ["TestStructure"],
                "WorkerOut": ["End"],
                "WorkInTypes": ["NeuralNetStructureTestCon"],
                "WorkOutTypes": ["EmptyContainer"]
            }
        }
    }
