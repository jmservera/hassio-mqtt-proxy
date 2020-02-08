import os

def get_fixture_path(filename):
    return os.path.join(os.path.dirname(__file__), "fixtures", filename)

def run_func(func, params, mock_out)->str:
    func(**params)
    return mock_out.getvalue()