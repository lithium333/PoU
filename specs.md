# 1 FRAME COMPOSITION

- given each bye in its hex format : 0xYZ
	Y: KEY - packet type
	Z: VALUE - content

- KEY LIST:
	(1,2,4,8) (7,B,D,E) -> VOID (Grey Encoding Error Suppression)
	0 0000 : RESERVED
		0x0A : CLOSE SEQUENCE ('\n' ASCII compatible)
	3 0011 : 4 bit address (4 bit addr. space)
		.1 e.g. 0x35 would refer to address 0x5
	4 0100 :
	5 0101 : 8 bit address (8 bit addr space, 4 MSB first, 4 MSB then)
		.1 e.g. (0x57 0x5A) would refer to device 0x7A and not 0xA7
		.2 always send two 0x5* packets to have valid stream
	6 0110 : 4 bit value (4 MSB of the byte)
		.1 e.g. 0x68 would set value 0x80 and not 0x08

	9 1001 : 8 bit value (4 MSB of the byte first, 4 MSB of the byte then)
		.1 e.g. (0x9A 0x93) would set 0xA3 and not 0x3A
		.2 always send 0x9* packets two by two
	A 1010 : SETUP 4 BIT ADDRESS
		.1 same specs as ADDR (0x3) & DATA (0x6)
	C 1100 : SETUP 8 BIT ADDRESS
		.1 same specs as ADDR (0x5) & DATA (0x9)
	F 1111 : RESERVED
		0xF0 : POWER OFF ALL (TAKE MEMORY values, SET ALL PWM registers to 0)
		0xF3 : UPDATE command (received DATA are stored to internal MCU memory, this command COPY them to PWM OUT regs)
		0xFF : BROADCAST as address

# 2 ALLOWED STREAM FORMATS

- each stream must have this format:
	(Address packet/s) - (Commands or data packets/s) - FINAL packet

- allowed examples

	COMMAND STREAMS:
		0xFF 0xF0 0x0A (power Off all lights)
		0x54 0X56 0xF3 0x0A (update PWM outputs of device at 0x46)
	DATA STREAMS:
		0x35 0x93 0x98 0x0A (set OUT1 of device 0x3 to value 0x38)
		0x51 0x53 0x6C 0x62 0x69 0x0A (set OUT1-2-3 of device 0x13 to values 0xC0 0x20 0x90)
