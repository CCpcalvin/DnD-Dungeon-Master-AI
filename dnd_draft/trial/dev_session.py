from LLMModel import LLMModel
import trial.ClassifyAction as ClassifyAction
from importlib import reload
import time

# Initialize the model once
print("Loading LLM (this will take a moment)...")
llm = LLMModel()


def reload_classify_action():
    """Reload only the ClassifyAction class while keeping the LLM in memory"""
    reload(ClassifyAction)  # Reload the module
    return ClassifyAction.ClassifyAction(llm.get_model())


def test_time():
    # Load the classify action
    classify_action = reload_classify_action()
    print("Ready!")
    t0 = time.time()
    classify_action.classify()
    t1 = time.time()

    print(t1 - t0)


test_time()
