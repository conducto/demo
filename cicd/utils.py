def magic_doc(doc_only=False):
    import importlib, inspect, os, traceback
    from conducto.shared.log import unindent

    st = traceback.extract_stack()
    func_name = st[-2].name
    module_name = os.path.basename(st[-2].filename).split(".py")[0]
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    docstring = func.__doc__
    if docstring is not None:
        code = inspect.getsource(func).split(docstring)[1]
    else:
        docstring = module.__doc__
        code = inspect.getsource(func)
    pretty_doc = unindent(docstring)
    pretty_code = code
    if pretty_code.startswith('"""'):
        pretty_code = pretty_code.lstrip('"')
    if pretty_code[0] != pretty_code.lstrip()[0]:
        pretty_code = unindent(pretty_code)
    pretty_code = f"\n```python\n{pretty_code}\n```"
    doc = pretty_doc + "\n" + pretty_code
    return pretty_doc if doc_only else doc
