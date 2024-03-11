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
        Initialize the TreeBuilder with the given repository path, valid extensions for files to analyze, and an optional starting path.

        Args:
        repo_path (str): The root path of the repository to analyze.
        valid_extensions (list): File extensions to include in the analysis.
        start_path (str, optional): Subpath within the repository from where to start the analysis.
        """
        self.repo_path = os.path.abspath(repo_path)
        self.valid_extensions = tuple(valid_extensions)
        self.start_path = os.path.join(self.repo_path, start_path) if start_path else self.repo_path
        self.docstring_pattern = re.compile(r'\s*("""|\'\'\')(.*?)(\1)', re.DOTALL | re.MULTILINE)
        self.class_pattern = re.compile(r'class\s+(\w+)(\((.*?)\))?:')
        self.method_pattern = re.compile(r'\sdef\s+(\w+)\s*\((.*?)\):')
        self.function_pattern = re.compile(r'^def\s+(\w+)\s*\(', re.MULTILINE)

    def build_tree(self):
        """
        Build a tree structure representing the repository, including information from code files and markdown documents.

        Returns:
        dict: A dictionary representing the structure and content of the repository.
        """
        return self.process_directory(self.start_path)

    def process_directory(self, directory):
        """
        Recursively process each file and subdirectory in the given directory.

        Args:
        directory (str): The directory to process.

        Returns:
        dict: Information about the processed files and subdirectories.
        """
        repo_info = {}
        for entry in os.scandir(directory):
            if entry.is_dir():
                repo_info.update(self.process_directory(entry.path))
            elif entry.is_file() and (entry.name.endswith(self.valid_extensions) or entry.name.endswith('.md')):
                file_info = self.extract_file_info(entry.path)
                relative_file_path = os.path.relpath(entry.path, self.start_path)
                repo_info[relative_file_path] = file_info
        return repo_info

    def extract_file_info(self, file_path):
        """
        Extract information from a single file, such as line count and, if applicable, classes, methods, and their docstrings.

        Args:
        file_path (str): The path to the file from which to extract information.

        Returns:
        dict: A dictionary containing the extracted information.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            return {'error': str(e)}

        if file_path.endswith('.md'):
            return {'project_summary': content.strip()}

        return {
            'line_count': content.count('\n') + 1,
            'classes': self.extract_classes(content),
            'functions': self.extract_definitions(content, self.function_pattern, is_class_method=False)
        }
        
    def extract_classes(self, content):
        classes = {}
        for class_match in self.class_pattern.finditer(content):
            class_name = class_match.group(1)
            class_body = self._get_block_content(content, class_match.end())
            methods = self.extract_definitions(class_body, self.method_pattern, is_class_method=True)
            classes[class_name] = {'methods': methods}
        return classes
        
    def extract_definitions(self, content, pattern, is_class_method):
        """
        Extract classes or functions and their docstrings from the content.

        Args:
        content (str): The content from which to extract information.
        definition_type (str): The type of definition to extract ('class' or 'def').

        Returns:
        dict: A dictionary of extracted definitions with their docstrings.
        """
        definitions = {}
        for match in pattern.finditer(content):
            name = match.group(1)
            docstring_match = self.docstring_pattern.search(content, match.end())
            docstring = docstring_match.group(2).strip() if docstring_match else ""
            if is_class_method:
                definitions[name] = {'docstring': docstring}
            else:
                definitions[name] = docstring
        return definitions

    def _get_block_content(self, content, start_pos):
        """
        Extract the content of a block (e.g., class or function body) starting from a given position.

        Args:
        content (str): The full content containing the block.
        start_pos (int): The start position of the block in the content.

        Returns:
        str: The extracted block content.
        """
        # Simplified implementation; a more robust implementation might be required for complex cases
        return content[start_pos:]

    @staticmethod
    def write_output(repo_info, output_file):
        """
        Write the analysis results to a specified output file.

        Args:
        repo_info (dict): The analysis results to write.
        output_file (str): The path to the output file.
        """
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("---- PROJECT SUMMARY ----\n\n")
            for filename, info in repo_info.items():
                file.write(f"File Analysis - {filename}:\nLine Count: {info.get('line_count', 'N/A')}\n\n")
                if 'project_summary' in info:
                    file.write("Document Content:\n")
                    file.write(f"{info['project_summary']}\n\n")
                if 'classes' in info:
                    file.write("Classes and Methods:\n")
                    for class_name, class_info in info['classes'].items():
                        file.write(f"Class: {class_name}\n")
                        for method, method_info in class_info['methods'].items():
                            file.write(f" - Method: {method}\nDocstring: {method_info['docstring']}\n\n")
                if 'functions' in info:
                    file.write("Standalone Functions:\n")
                    for function, docstring in info['functions'].items():
                        file.write(f"Function: {function}\nDocstring: {docstring}\n\n")
                file.write("-" * 40 + "\n")