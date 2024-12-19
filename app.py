import argparse
import toml
import re
from math import sqrt
 
class TranslationError(Exception):
    pass

def verify_name(name: str):
    return isinstance(name, str) and re.fullmatch(r"[_a-zA-Z][_a-zA-Z0-9]*", name)

def verify_expr(expr: str):
    return isinstance(expr, str) and re.fullmatch(r"\^\((\S+)\s*(\S+)\s*(\d*(?:\.\d*)?)?\)", expr)
    
def translate(obj, scope: dict={}, depth=0, root: bool=False):
    if isinstance(obj, dict):
        result = []
        if not root:
            result.append("{")
        for key, value in obj.items():
            if not verify_name(key):
                raise NameError(f"Names should be [_a-zA-Z][_a-zA-Z0-9]* but \"{key}\" found")
            value = translate(value, scope, depth+1)
            if root and isinstance(value, (int, float)):
                scope.update({key: value})
            result.append(f"{ f"const {key} = " if root else f"{' ' * 4 * depth}{key} : "}{value}{";" if root else ","}")
        if not root:
            result.append(f"{' ' * 4 * (depth - 1)}}}")
        return "\n".join(result)
    elif isinstance(obj, (int, float)):
        return obj
    elif isinstance(obj, str):
        expr_match = verify_expr(obj)
        if expr_match:
            op, name, val = expr_match.groups()
            if name not in scope:
                raise NameError(f"const {name} not found")
            out_type = int if isinstance(scope[name], int) and val.isnumeric() else float
            if op == "+":
                return scope[name] + out_type(val)
            elif op == "-":
                return scope[name] - out_type(val)
            elif op == "sqrt":
                return sqrt(scope[name])
            else:
                raise ValueError(f"Unknown operator {op}")
        else:
            raise NameError(f"Wrong expr: {obj}")
    elif isinstance(obj, list) and len(obj) == 1:
        return translate(obj[0], scope, depth)
    else:
        raise TranslationError(f'Unknown type {type(obj)} at line: "{obj}"')

def main():
    parser = argparse.ArgumentParser(description="Custom configuration language tool.")
    parser.add_argument("input", help="Path to input TOML file.")
    parser.add_argument("output", help="Path to output file.")
    args = parser.parse_args()

    with open(args.input, 'r', encoding="utf-8") as f:
        config = toml.load(f)

    config_lang_output = translate(config, root=True)

    with open(args.output, 'w') as f:
        f.write(config_lang_output)

    print("Transformation successful. Output written to:", args.output)

if __name__ == "__main__":
    main()