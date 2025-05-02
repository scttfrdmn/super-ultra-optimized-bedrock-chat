#!/bin/bash
cat > temp_venv/bin/ultra-bedrock-chat << "EOL"
#!/Users/scttfrdmn/src/ultra-optimized-bedrock-chat/temp_venv/bin/python3.13
# -*- coding: utf-8 -*-
import re
import sys
from bedrock_chat.cli import app
if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(app())
EOL

cat > temp_venv/bin/ultra-optimized-bedrock-chat << "EOL"
#!/Users/scttfrdmn/src/ultra-optimized-bedrock-chat/temp_venv/bin/python3.13
# -*- coding: utf-8 -*-
import re
import sys
from bedrock_chat.cli import app
if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(app())
EOL

chmod +x temp_venv/bin/ultra-bedrock-chat
chmod +x temp_venv/bin/ultra-optimized-bedrock-chat
