"""nginx configuration formatter. Based on nginxfmt for python 2.7.
This code provides functions to format nginx configuration files.
I wrote this code for an ansible action plugin and didn't refactor it now."""
import codecs
import os
import re

INDENTATION = ' ' * 4
NGINX_CONF_PATH_PREFIX = "~/templates/"

TEMPLATE_VARIABLE_OPENING_TAG = '___TEMPLATE_VARIABLE_OPENING_TAG___'
TEMPLATE_VARIABLE_CLOSING_TAG = '___TEMPLATE_VARIABLE_CLOSING_TAG___'


def strip_line(single_line):
    """Strips the line and replaces neighbouring whitespaces with single space (except when within quotation marks)."""
    single_line = single_line.strip()
    if single_line.startswith('#'):
        return single_line

    within_quotes = False
    parts = []
    for part in re.split('"', single_line):
        if within_quotes:
            parts.append(part)
        else:
            parts.append(re.sub(r'[\s]+', ' ', part))
        within_quotes = not within_quotes
    return '"'.join(parts)


def check_skip_include(line, exclude_patterns=None):
    """
        Checks need skipping include and leave as is or load data from file
        Returns:
        The return bool. True if found line in exclude_patterns , False otherwise.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    full_regexp = ''
    for r in exclude_patterns:
        full_regexp += '(' + r + ')' + '|'
    full_regexp = full_regexp.strip('|')
    pattern = re.compile(full_regexp)

    if pattern.match(line):
        return True
    else:
        return False


def apply_variable_template_tags(line):
    """Replaces variable indicators ${ and } with tags, so subsequent formatting is easier."""
    return re.sub(r'\${\s*(\w+)\s*}',
                  TEMPLATE_VARIABLE_OPENING_TAG + r"\1" + TEMPLATE_VARIABLE_CLOSING_TAG,
                  line,
                  flags=re.UNICODE)


def strip_variable_template_tags(line):
    """Replaces tags back with ${ and } respectively."""
    return re.sub(TEMPLATE_VARIABLE_OPENING_TAG + r'\s*(\w+)\s*' + TEMPLATE_VARIABLE_CLOSING_TAG,
                  r'${\1}',
                  line,
                  flags=re.UNICODE)


def clean_lines(orig_lines):
    """Strips the lines and splits them if they contain curly brackets."""
    cleaned_lines = []
    for line in orig_lines:
        line = strip_line(line)
        line = apply_variable_template_tags(line)
        if line == "":
            cleaned_lines.append("")
            continue
        else:
            cleaned_lines.append(strip_variable_template_tags(line))
    return cleaned_lines


def join_opening_bracket(lines):
    """When opening curly bracket is in it's own line (K&R convention), it's joined with precluding line (Java)."""
    modified_lines = []
    for i in range(len(lines)):
        if i > 0 and lines[i] == "{":
            modified_lines[-1] += " {"
        else:
            modified_lines.append(lines[i])
    return modified_lines


def perform_indentation(lines):
    """Indents the lines according to their nesting level determined by curly brackets."""
    indented_lines = []
    current_indent = 0
    for line in lines:
        if not line.startswith("#") and line.endswith('}') and current_indent > 0:
            current_indent -= 1

        if line != "":
            indented_lines.append(current_indent * INDENTATION + re.sub(r'^[\s]+', '', line))
        else:
            indented_lines.append("")

        if not line.startswith("#") and line.endswith('{'):
            current_indent += 1

    return indented_lines


def load_includes(lines, exclude_patterns=None):
    """Recursive load nested include."""
    if exclude_patterns is None:
        exclude_patterns = []

    modified_lines = []
    # pattern for catch include directive
    pattern = re.compile(r'\s*include')
    # pattern for access config, which creating from sys-deploy
    for line in lines:
        # if match, load file and go to next iteration
        if pattern.match(line):
            # If this is access file, then generated access.sh. Skip it
            if check_skip_include(line, exclude_patterns=exclude_patterns):
                modified_lines.append(line)
                continue
            # Check include directive level
            spaces = re.search('(^\s*).*', line).group(1)
            # strip path to file. Leave only the filename
            config_f = re.sub('^\/etc\/nginx\/', '', line.split()[1].strip(';'))
            # if file not found in repo, then it's something empty file which was include
            if not os.path.isfile(os.path.expanduser(NGINX_CONF_PATH_PREFIX + config_f)):
                continue
            for nested_line in format_config_file(config_f, includes=True, exclude_patterns=exclude_patterns):
                # if directive was not first level, than add spaces
                if spaces:
                    nested_line = spaces + nested_line
                modified_lines.append(nested_line)
            continue
        modified_lines.append(line)
    return modified_lines


def format_config_contents(contents, includes=False, exclude_patterns=[]):
    """Accepts the string containing nginx configuration and returns formatted one. Adds newline at the end."""
    lines = contents.splitlines()
    lines = join_opening_bracket(lines)
    lines = perform_indentation(lines)

    lines = load_includes(lines, exclude_patterns=exclude_patterns)
    if includes:
        return lines

    text = '\n'.join(lines)

    for pattern, substitute in ((r'\n{3,}', '\n\n\n'), (r'^\n', ''), (r'\n$', '')):
        text = re.sub(pattern, substitute, text, re.MULTILINE)

    return text + '\n'


def format_config_file(file_path, includes=False, exclude_patterns=[]):
    """
    Performs the formatting on the given file. The function tries to detect file encoding first.
    :param file_path: path to original nginx configuration file. This file will be overridden.
    :param includes: bool. Usage for loading nested nginx config
    :param exclude_patterns: List with line's regexps which need leave as is
    """
    encodings = ('utf-8', 'latin1')
    config_path = os.path.expanduser(NGINX_CONF_PATH_PREFIX + file_path)

    chosen_encoding = None

    for enc in encodings:
        try:
            with codecs.open(config_path, 'r', encoding=enc) as rfp:
                original_file_content = rfp.read()
            chosen_encoding = enc
            break
        except (FileNotFoundError, IOError):
            raise FileNotFoundError(f'Filed open nginx_config_file: {file_path}. Error: FileNotFoundError')
    if chosen_encoding is None:
        raise UnicodeEncodeError(f'None of encodings {encodings} are valid for file {file_path}')

    assert original_file_content is not None

    if includes:
        return format_config_contents(original_file_content, includes, exclude_patterns=exclude_patterns)
    else:
        return format_config_contents(original_file_content, exclude_patterns=exclude_patterns)
