# griffe_inherited_method_crossrefs

Griffe extension to replace docstrings of inherited methods with cross-references to parent

For example, if a class `foo.Child` inherits the method `do_something` from `bar.Parent`, then in the generated documentation, the docstring of `Child.do_something` will appear similar to

> Inherited from [bar.Parent](/link/to/bar.Parent.do_something)

whereas the docstring of `bar.Parent.do_something` will be unaffected.

## Installation

```python
pip install griffe-inherited-method-crossrefs
```

## Usage

After installation, to use this extension with Mkdocs and mkdocstrings, add the following to your `mkdocs.yml`:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
          - griffe_inherited_method_crossrefs
```