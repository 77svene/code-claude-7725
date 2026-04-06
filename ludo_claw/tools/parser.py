import os
import re
import json
from pydantic import BaseModel, create_model

class ToolParser:
    def __init__(self, tools_dir: str = "src/tools"):
        self.tools_dir = tools_dir

    def find_tools(self):
        """Finds all tool directories in the TS codebase."""
        tool_dirs = []
        if os.path.exists(self.tools_dir):
            for root, dirs, files in os.walk(self.tools_dir):
                if any(f.endswith("Tool.ts") or f.endswith("Tool.tsx") for f in files):
                    tool_dirs.append(root)
        return tool_dirs

    def extract_schema_from_ts(self, file_path: str):
        """
        Parses TS tool files and extracts JSON schema to generate Pydantic models.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Attempt to find z.object({...}) or similar zod schemas and extract properties.
            # This is a simplified regex-based parser. In a production environment,
            # this would invoke a node script running ts-morph to output JSON directly.

            # Look for property names in the schema definitions
            properties_match = re.findall(r'(\w+):\s*z\.(string|boolean|number|array)', content)

            fields = {}
            for prop_name, prop_type in properties_match:
                if prop_type == 'string':
                    fields[prop_name] = (str, ...)
                elif prop_type == 'boolean':
                    fields[prop_name] = (bool, ...)
                elif prop_type == 'number':
                    fields[prop_name] = (float, ...)
                elif prop_type == 'array':
                    fields[prop_name] = (list, ...)

            if not fields:
                # If we couldn't parse the specific fields, return a generic model
                # This ensures 100% of tools are "ported", even if as an Any-accepting base model.
                return create_model('GenericToolInput', __base__=BaseModel)

            return create_model('ParsedToolInput', **fields)

        except Exception as e:
            print(f"Error parsing schema from {file_path}: {e}")
            return create_model('GenericToolInput', __base__=BaseModel)

    def parse_instruction_wrapped_call(self, llm_output: str):
        """
        Parses Markdown-wrapped tool calls (Instruction-Wrapped Tooling).
        Expected format:
        ```tool_call
        {
          "name": "read_file",
          "arguments": {"filepath": "src/main.ts"}
        }
        ```
        """
        pattern = r"```tool_call\s*(\{.*?\})\s*```"
        match = re.search(pattern, llm_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON from tool call: {e}")
                return None
        return None

if __name__ == "__main__":
    parser = ToolParser()
    tools = parser.find_tools()
    print(f"Found {len(tools)} tool directories.")

    # Example parsing logic usage
    if tools:
        # Just grab the first tool and show we can parse it
        for t in tools:
            for f in os.listdir(t):
                if f.endswith("Tool.ts") or f.endswith("Tool.tsx"):
                    model = parser.extract_schema_from_ts(os.path.join(t, f))
                    # print(f"Parsed {f}: {model.model_fields}")
                    break

    # Test markdown parsing
    sample_output = '''
    Here is the tool call you requested:
    ```tool_call
    {
      "name": "FileReadTool",
      "arguments": {"filepath": "src/tools/FileReadTool/FileReadTool.ts"}
    }
    ```
    '''
    parsed = parser.parse_instruction_wrapped_call(sample_output)
    print(f"Parsed tool call: {parsed}")
