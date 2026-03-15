class Token:
    def __init__(self, value, token_type, line_num, column):
        self.value = value
        self.type = token_type
        self.line_num = line_num
        self.column = column

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code 
        self.lines = source_code.splitlines()

    def strip_comments(self, line):
        """
        Removes everything after the '#' character and cleans whitespace.
        """
        return line.split('#')[0].rstrip()

    def get_token_stream(self):
        """
        The main loop that processes the file line-by-line.
        """
        all_tokens = []
        
        for line_idx, raw_line in enumerate(self.lines):
            line_num = line_idx + 1
            clean_line = self.strip_comments(raw_line)
            
            if not clean_line.strip():
                continue
            

            words = self._split_line(clean_line)
            for word in words:
                all_tokens.append(Token(word, "UNKNOWN", line_num, 0))
                
        return all_tokens

    def _split_line(self, line):
        """
        Helper to handle commas and spaces as delimiters.
        """
        return line.replace(',', ' ').split()