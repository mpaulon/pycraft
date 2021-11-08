import sys


def hexprint(data, file=sys.stdout):
	for start in range(0, len(data), 16):
		line = ' '.join(f'{byte:02X}' for byte in data[start:start+16])
		if len(line) < 47:
			line += ' ' * (47 - len(line))
		line += '  '
		for byte in data[start:start+16]:
			if 32 <= byte <= 127:
				line += chr(byte)
			else:
				line += '.'
		print(f'{start:08X}: {line}', file=file)
