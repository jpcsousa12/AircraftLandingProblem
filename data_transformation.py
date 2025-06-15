import os

def raw2dat(path):
    repo_root = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(repo_root, 'data')
    os.makedirs(output_path, exist_ok=True)
    files = os.listdir(path)
    for file in files:
        if not file.endswith('.txt'):
            continue

        with open(f"{path}/{file}") as f:
            # Flatten all numbers into a single list (int or float as needed)
            tokens = []
            for line in f:
                if line.strip():
                    for t in line.strip().split():
                        tokens.append(float(t) if '.' in t else int(t))

        idx = 0
        P = tokens[idx]; idx += 1
        freeze = tokens[idx]; idx += 1  # skip freeze time

        Ai, Ei, Ti, Li, gi, hi, S = [], [], [], [], [], [], []

        for i in range(P):
            Ai.append(int(tokens[idx])); idx += 1
            Ei.append(int(tokens[idx])); idx += 1
            Ti.append(int(tokens[idx])); idx += 1
            Li.append(int(tokens[idx])); idx += 1
            gi.append(int(tokens[idx])); idx += 1
            hi.append(int(tokens[idx])); idx += 1
            S.append([int(x) for x in tokens[idx:idx+P]]); idx += P

        content_lines = [
            f'P = {P};',
            f'Ai = [{",".join(map(str, Ai))}];',
            f'Ei = [{",".join(map(str, Ei))}];',
            f'Ti = [{",".join(map(str, Ti))}];',
            f'Li = [{",".join(map(str, Li))}];',
            f'gi = [{",".join(map(str, gi))}];',
            f'hi = [{",".join(map(str, hi))}];',
            'S = ['
        ]
        for row in S:
            content_lines.append('  [' + ','.join(map(str, row)) + '],')
        content_lines.append('];')

        output_file = os.path.splitext(file)[0] + '.dat'
        with open(os.path.join(output_path, output_file), 'w') as out:
            out.write('\n'.join(content_lines))
        print(f"Wrote {output_file} to {output_path}")

# Usage:
raw2dat("raw_data")
