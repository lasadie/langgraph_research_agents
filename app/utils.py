import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_report_to_markdown(final_report: str) -> str:
    """
    Parse the final report text into proper markdown format with headers.
    :param final_report: The complete final report
    :return: Properly formatted markdown string
    """
    
    # Split the report into sections based on common patterns
    lines = final_report.split('\n')
    markdown_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            markdown_lines.append('')
            continue
            
        # Check for section headers with content on the same line
        if line.startswith('Research Report:'):
            # Main title
            title = line.replace('Research Report:', '').strip()
            markdown_lines.append(f'# {title}')
        elif line.startswith('Executive Summary:'):
            content = line.replace('Executive Summary:', '').strip()
            markdown_lines.append('## Executive Summary')
            if content:
                markdown_lines.append('')
                markdown_lines.append(content)
        elif line.startswith('Introduction:'):
            content = line.replace('Introduction:', '').strip()
            markdown_lines.append('## Introduction')
            if content:
                markdown_lines.append('')
                markdown_lines.append(content)
        elif line.startswith('Main Findings:'):
            content = line.replace('Main Findings:', '').strip()
            markdown_lines.append('## Main Findings')
            if content:
                markdown_lines.append('')
                markdown_lines.append(content)
        elif line.startswith('Conclusion:'):
            content = line.replace('Conclusion:', '').strip()
            markdown_lines.append('## Conclusion')
            if content:
                markdown_lines.append('')
                markdown_lines.append(content)
        elif line.startswith('Key Takeaways:'):
            content = line.replace('Key Takeaways:', '').strip()
            markdown_lines.append('## Key Takeaways')
            if content:
                markdown_lines.append('')
                markdown_lines.append(content)
        elif line.startswith('References:'):
            markdown_lines.append('## References')
            # References section might be empty here, content comes in subsequent lines
        elif line.endswith(':'):
            # Generic section header
            header = line.rstrip(':')
            markdown_lines.append(f'### {header}')
        else:
            # Regular content line
            markdown_lines.append(line)
    
    return '\n'.join(markdown_lines)