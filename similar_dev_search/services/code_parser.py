from typing import Dict, List

import enry
from tree_sitter import Language, Parser, Tree
from tree_sitter import Node

java_imports_used_methods_query_string = """
(import_declaration (scoped_identifier (identifier)) @name)
(import_declaration (identifier) @name)
(import_declaration ((scoped_identifier (identifier)) (asterisk)) @name)
(package_declaration (identifier) @name)
(method_invocation name: (identifier) @function.call)
(local_variable_declaration declarator: (variable_declarator name: (identifier) @name))
"""

# query of names of created packages, classes, interfaces, methods, arguments, fields
java_names_query = """
(package_declaration (scoped_identifier (identifier)) @name)
(class_declaration name: (identifier) @name)
(interface_declaration name: (identifier) @name)
(method_declaration name: (identifier) @name)
(method_declaration (formal_parameters(formal_parameter (identifier) @name)))
(field_declaration declarator: (variable_declarator name: (identifier) @name))
"""

# query of imports, called functions
python_imports_used_methods_query_string = """
(import_from_statement (dotted_name (identifier)) @dotted_name)
(import_statement (dotted_name (identifier)) @dotted_name)
(aliased_import (dotted_name (identifier)) @dotted_name)
(call function: (identifier) @function.call)
"""

# query of names of classes, functions, fields
python_names_query_string = """
(class_definition name: (identifier) @name)
(function_definition name: (identifier) @function.def)
(expression_statement (assignment left: (identifier) @name))
"""

# query of imports, called functions
js_imports_used_methods_query_string = """
(expression_statement (member_expression) @name)
(expression_statement (call_expression (member_expression (call_expression (import) (arguments (string (string_fragment)
 @name)))
    (property_identifier)) (arguments (arrow_function (formal_parameters (identifier) @name) (statement_block)))))
(import_statement (import_clause (identifier) @name) (string (string_fragment)) @name)
(import_statement (import_clause (namespace_import (identifier) @name)) (string (string_fragment) @name))
(import_statement (import_clause (named_imports (import_specifier (identifier)) @name))
(string (string_fragment) @name))
(import_statement (import_clause (named_imports (import_specifier (identifier)) (import_specifier (identifier)
(identifier) @name)))
    (string (string_fragment)))
"""

# query of names of classes, functions, fields
js_names_query_string = """
(assignment_expression (identifier) @name) (variable_declaration (variable_declarator (
identifier) @name)) (lexical_declaration (variable_declarator (identifier) @name)) (expression_statement (
call_expression (member_expression (call_expression (import) (arguments (string (string_fragment) @name))) (
property_identifier)) (arguments (arrow_function (formal_parameters (identifier) @name) (statement_block))))) (
expression_statement (member_expression) @name) (class_declaration name: (identifier) @name) (function_declaration
    name: (identifier) @name) """


class CodeEntitiesParser:
    @staticmethod
    def process_query(query_str, language: Language, code: bytes, root_node: Node) -> List[str]:
        """
        Processes query using query_str for LANGUAGE.

        :param query_str: query string to extract info.
        :param language: Language instance.
        :param code: Part of code represented in bytes(str) utf8 encoding.
        :param root_node: Root of the parsed tree.
        :return: Returns list of queried results.
        """
        query = language.query(query_str)
        return list(set([code[x[0].start_byte: x[0].end_byte].decode() for x in query.captures(root_node)]))

    @staticmethod
    def process_tree_sitter(language: str, code: bytes, tree, tree_sitter_build_path: str) -> Dict:
        """
        Process lines of code returning dict.

        :param language: Language instance.
        :param code: Part of code represented in bytes(str) utf8 encoding.
        :param tree: Parsed tree.
        :param tree_sitter_build_path: Path to tree_sitter build folder.
        :return: Returns dict with list of imports and names.
        """
        if language == "unknown":
            return {"imports": [], "names": []}
        parse_lang = Language(tree_sitter_build_path + "my-languages.so", language.lower())
        choice = {
            "java": [java_imports_used_methods_query_string, java_names_query],
            "python": [python_imports_used_methods_query_string, python_names_query_string],
            "javascript": [js_imports_used_methods_query_string, js_names_query_string]
        }
        imports_and_names = {
            "imports": CodeEntitiesParser.process_query(choice[parse_lang.name][0], parse_lang, code, tree.root_node),
            "names": CodeEntitiesParser.process_query(choice[parse_lang.name][1], parse_lang, code, tree.root_node)
        }
        return imports_and_names

    @staticmethod
    def parse_code(code: bytes, parser: Parser) -> Tree:
        """
        Parses code_str using created tree-sitter parser.

        :param code: Lines of code in bytes.
        :param parser: Specified code parser.
        :return: Returns parsed tree.
        """
        return parser.parse(code)

    @staticmethod
    def go_parse(language: str, code: bytes, tree_sitter_build_path: str):
        parser = Parser()
        parser.set_language(Language(tree_sitter_build_path + "my-languages.so", language.lower()))
        tree = CodeEntitiesParser.parse_code(code, parser)
        return CodeEntitiesParser.process_tree_sitter(language, code, tree, tree_sitter_build_path)

    @staticmethod
    def parse_file(languages: List[str], code_str: str, tree_sitter_build_path: str) -> Dict:
        """
        Function processes pipeline for parsing file.

        :param languages: List of languages of file.
        :return: Returns dictionary with used imports and named fields, variables and methods.
        """
        code = bytes(code_str, "utf8")
        language = list({"java", "javascript", "python"} & set([x.lower() for x in languages]))
        language = language[0] if len(language) > 0 else "unknown"
        if language != "unknown":
            return CodeEntitiesParser.go_parse(language, code, tree_sitter_build_path)
        return {"imports": [], "names": []}


class LanguagesProvider:
    @staticmethod
    def get_language_by_name_and_content(file_name: str, content: str) -> str:
        """
        Get language name by a file name and a file content.

        :param file_name: The file name with an extension.
        :param content: The content of the file.
        :return: The language name.
        """
        language = enry.get_language(file_name, str.encode(content))
        if language == "":
            return "Other"
        return language

    @staticmethod
    def get_language(filename: str, file_path: str) -> str:
        """
        Get language by a file name and a file path.

        :param filename: The file name with an extencion.
        :param file_path: The path to the file.
        :return: The language name.
        """
        with open(file_path) as f:
            try:
                return LanguagesProvider.get_language_by_name_and_content(filename, f.read())
            except UnicodeDecodeError:
                return "Other"
