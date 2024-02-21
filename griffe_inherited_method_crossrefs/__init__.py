"""Griffe extension to add cross-references to inherited method docstrings.

Derived from [griffe-inherited-docstrings](https://github.com/mkdocstrings/griffe-inherited-docstrings/blob/cf7cdd2ba000d3e40d5d13affc6c2bc1829ac92d/src/griffe_inherited_docstrings/extension.py).
"""

import contextlib
import copy
from typing import TYPE_CHECKING
from griffe import Extension, Docstring, Function
from griffe.exceptions import AliasResolutionError

if TYPE_CHECKING:
    from griffe import Module, Object
    

def _inherited_method_crossrefs(obj: "Object") -> None:
    if obj.is_module:
        for member in obj.members.values():
            if not member.is_alias:
                with contextlib.suppress(AliasResolutionError):
                    _inherited_method_crossrefs(member)  # type: ignore[arg-type]
    if obj.is_class:
        for member in obj.inherited_members.values():
            # Inherited members are always aliases, though?
            if member.is_alias and member.target.is_function: 
                # I had tried to just replace `member.docstring`, but that 
                # resulted in the parent docstring being altered as well. 
                # I assume this is because `member` is an alias. 
                #
                # Instead, create a new member for the inherited method,
                # populate it with the appropriate attributes, change its 
                # docstring, and then replace the alias member with the new 
                # member.
                new_member = Function(
                    member.name, 
                    parameters=member.target.parameters, 
                    returns=member.target.returns,
                    decorators=member.target.decorators,
                )
                
                # Problems:
                #  1) `canonical_path` includes private modules, so it doesn't 
                #     reflect the usual import path of an object, if that object 
                #     is imported from (say) `__init__.py` of the package. For 
                #     now, we'll just reference the parent object's name without 
                #     the full path.
                #  2) While `member.target.path` appears to be correct 
                #     when printed from within this function, if we use it as 
                #     the crossref link, the docs end up linking to the wrong 
                #     place sometimes. For example, if A is the parent of B and 
                #     C, both of which inherit method `m` from A, then the 
                #     "Inherited from" docstring from B may link to C. 
                #     The first part of the crossref (the printed label) is 
                #     not affected. This all suggests that the problem 
                #     might be with the mkdocstrings handler, not Griffe.
                #     For now, we link to the parent object, rather than the 
                #     specific method of the parent. This seems to work.
                
                #crossref_path = member.target.path
                crossref_path = member.target.parent.path
                #crossref_str = member.target.parent.path
                crossref_str = member.target.parent.name
                new_member.docstring = Docstring(
                    f"Inherited from [`{crossref_str}`][{crossref_path}]."
                )

                # Make sure properties, abstractmethods, etc. get labeled 
                new_member.labels = member.target.labels
                # This is a (hopefully temporary) hack since Griffe doesn't
                # add "abstractproperty" to member labels. 
                # 
                # Also adds the label to the target member, since the preceding  
                # line only assigns a reference to the new member.
                if any(str(decorator.value) == "abstractproperty" 
                       for decorator in member.target.decorators):
                    new_member.labels.add("abstractproperty")
                    
                member.parent.set_member(member.name, new_member)

class InheritedMethodCrossrefs(Extension):
    """Griffe extension for replacing docstrings of inherited methods with crossrefs."""
    
    def on_package_loaded(self, *, pkg: "Module") -> None:
        """Inherit docstrings from parent classes once the whole package is loaded."""
        _inherited_method_crossrefs(pkg)