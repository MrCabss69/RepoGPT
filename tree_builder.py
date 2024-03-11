# Created by: [@MrCabss69]
# Creation date: Mon Mar 11 2024
# --- TreeBuilder ---
# Analyze files in a code repository, extracting information about the number of lines,
# the classes, methods and functions, including their docstrings.

import os
import re

class TreeBuilder:
    
    def __init__(self, repo_path, valid_extensions, start_path=''):
        """
        Initializes the repository parser with the repository path, valid file extensions, and the home path.

        Parameters:
            repo_path (str): The path to the repository that will be analyzed.
            valid_extensions (list): A list of valid file extensions for scanning.
            start_path (str, optional): The subpath within the repository from which to start the analysis.
        """
        self.repo_path = repo_path
        self.valid_extensions = tuple(valid_extensions)
        self.start_path = start_path
        self.docstring_pattern = re.compile(r'\s*("""|\'\'\')(.*?)(\1)', re.DOTALL | re.MULTILINE)
        self.class_pattern = re.compile(r'class\s+(\w+)\s*[\(:]')
        self.method_pattern = re.compile(r'def\s+(\w+)\s*\(')
        self.function_pattern = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

    def extract_file_info(self, file_path):
        """
        Extracts detailed information from a file, including line count, classes with their methods, and independent functions.

        Parameters:
            file_path (str): The path to the file from which the information will be extracted.

        Returns:
            dict: A dictionary with the count of lines, classes (and their methods) and functions.
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        line_count = content.count('\n') + 1
        classes = self.extract_classes(content)
        functions = self.extract_functions(content)
        return {'line_count': line_count, 'classes': classes, 'functions': functions}

    def extract_classes(self, content):
        """
        Extracts information about classes and their methods from the provided content.

        Parameters:
            content (str): The content of the file from which the classes and methods will be extracted.

        Returns:
            dict: A dictionary of classes, each with their respective methods and docstrings.
        """
        classes = {}
        class_matches = list(self.class_pattern.finditer(content))
        for i, class_match in enumerate(class_matches):
            class_name = class_match.group(1)
            class_body_start = class_match.end()
            if i + 1 < len(class_matches):
                class_body_end = class_matches[i + 1].start()
            else:
                class_body_end = len(content)

            class_content = content[class_body_start:class_body_end]
            methods = {}

            for method_match in self.method_pattern.finditer(class_content):
                method_name = method_match.group(1)
                method_body_start = method_match.end()
                next_method_match = next(self.method_pattern.finditer(class_content, method_body_start), None)
                method_body_end = next_method_match.start() if next_method_match else len(class_content)
                method_content = class_content[method_body_start:method_body_end]
                docstring_match = self.docstring_pattern.search(method_content)
                docstring = docstring_match.group(2).strip() if docstring_match else ""
                methods[method_name] = docstring

            classes[class_name] = methods
        return classes


    def extract_functions(self, content):
        """
        Extracts information about independent functions from the provided content.

        Parameters:
            content (str): The content of the file from which the functions will be extracted.

        Returns:
            dict: A dictionary of functions and their respective docstrings.
        """
        functions = {}
        for function_match in self.function_pattern.finditer(content):
            function_name = function_match.group(1)
            docstring = self.extract_docstring(content[function_match.end():]).strip()
            functions[function_name] = docstring
        return functions

    def extract_docstring(self, content):
        """
        Extracts the docstring immediately following the given content.

        Parameters:
            content (str): The content from which the docstring will be extracted.

        Returns:
            str: The found docstring or an empty string if none are found.
        """
        match = self.docstring_pattern.search(content)
        return match.group(2) if match else ""

    def summarize_project_documents(self):
        """
        Summary of key project documents, such as README.md, IDEA.md, and DEVELOPING.md.

        Returns:
            dict: A dictionary with document names as keys and their contents as values.
        """
        summaries = {}
        for doc in ['README.md', 'IDEA.md', 'DEVELOPING.md']:
            try:
                with open(os.path.join(self.repo_path, doc), 'r', encoding='utf-8') as file:
                    summaries[doc] = file.read().strip()
            except FileNotFoundError:
                pass
        return summaries

    def build_tree(self):
        """
        Processes the repository by parsing files that match the specified extensions and summarizes the project documents.

        Returns:
            dict: A dictionary with detailed information about each processed file and summaries of project documents.
        """
        repo_info = {'project_summary': self.summarize_project_documents()}
        for root, _, files in os.walk(os.path.join(self.repo_path, self.start_path), topdown=True):
            for file in files:
                if file.endswith(self.valid_extensions) or file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    file_info = self.extract_file_info(file_path)
                    relative_file_path = os.path.relpath(file_path, self.start_path)
                    repo_info[relative_file_path] = file_info
        return repo_info

    @staticmethod
    def write_output(repo_info, output_file):
        """
        Writes the analysis results to an output file in text format.

        Parameters:
            repo_info (dict): The results of the analysis of each processed file and the summaries of the project documents.
            output_file (str): The path to the output file where the results will be written.
        """
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("---- PROJECT SUMMARY ----\n\n")
            for doc, summary in repo_info['project_summary'].items():
                file.write(f"{doc}:\n{summary}\n\n")

            for filename, info in repo_info.items():
                if filename == 'project_summary':
                    continue
                file.write(f"File Analysis - {filename}:\nLine Count: {info['line_count']}\n\n")
                if info['classes']:
                    file.write("Classes and Methods:\n")
                    for class_name, methods in info['classes'].items():
                        file.write(f"Class: {class_name}\n")
                        for method, docstring in methods.items():
                            file.write(f" - Method: {method}\nDocstring: {docstring}\n\n")
                    file.write("\n")
                if info['functions']:
                    file.write("Standalone Functions:\n")
                    for function, docstring in info['functions'].items():
                        file.write(f"Function: {function}\nDocstring: {docstring}\n\n")
                    file.write("-" * 40 + "\n")