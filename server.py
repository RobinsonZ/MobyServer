import socket, struct
import navio.pwm, navio.util, navio.leds

# util.check_apm()

PORT = 5001
IP = ''
TIMEOUT = 0.1 # seconds

ENABLE_FLAG = 0b10000000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))
sock.settimeout(TIMEOUT)

conn = False
enable = False
last_seq = 0

led = navio.leds.Led()
pwms = [navio.pwm.PWM(chan) for chan in range(0, 14)]

for pwm in pwms:
    pwm.initialize()

if __name__ == '__main__':
    while True:
        try:
            packet, addr = sock.recvfrom(128) # the packet is actually 121 bytes, but next power of 2
            data = struct.unpack("!qB14d", packet)

            seq = data[0]
            cmd = data[1]
            pwm_throts = data[2:]
            if seq > last_seq:
                last_seq = seq

                if not conn:
                    print("Connected from " + str(addr))
                    conn = True

                if ENABLE_FLAG & cmd != 0:
                    if not enable:
                        print("!!!! ENABLED !!!!")
                        enable = True

                    for pwm, throt in zip(pwms, pwm_throts):
                        if throt >= 0:
                            pwm.set_period(50)
                            pwm.enable()
                            pwm.set_duty_cycle(throt)
                        elif pwm.is_enabled:
                            pwm.disable()

                else:
                    if enable:
                        print("Disabling")
                        enable = False
                        for pwm in pwms:
                            if pwm.is_enabled:
                                pwm.disable()

            else:
                print("Invalid sequence number " + str(seq) + ", should be greater than " + str(last_seq))
                conn = False
                enable = False
        except socket.timeout:
            if conn:
                print("Did not receive packet in time, disabling outputs")
                conn = False
                enable = False

        if conn:
            if enable:
                led.setColor("Red")
            else:
                led.setColor("Green")
        else:
            led.setColor("Yellow")
