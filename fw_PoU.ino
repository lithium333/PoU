// PORTS
#define PWMPORT_0 3
#define PWMPORT_1 5
#define PWMPORT_2 6
#define PWMPORT_3 9
#define PWMPORT_4 10
#define PWMPORT_5 11
#define MAX_PORTS 6

// KEYs
#define KCODE_ADDR4 0x3 // Address 4-bit
#define KCODE_ADDR8 0x5 // Address 8-bit
#define KCODE_DATA4 0x6 // Data 4-bit (MSB)
#define KCODE_DATA8 0x9 // Data 8-bit

// RESERVED COMMANDS
#define KCODE_RES_END 0x0A // end of stream
#define KCODE_RES_OFF 0xF0 // POWER OFF ALL command
#define KCODE_RES_UPD 0xF3 // UPDATE command
#define KCODE_RES_BRD 0xFF // BROADCAST dest

//0 idle : expected address
//1 wait 2nd part of base 8 addr
//2 wait data, command or end of stream
//3 wait 2nd part of 8 bit data packet

volatile uint8_t fsm_state=0;
uint8_t own_addr_base4;
uint8_t own_addr_base8;
uint8_t addr_read;
uint8_t data_read[MAX_PORTS];
uint8_t reg_port0=0;
uint8_t port_cnt=0;

void setup() {
  Serial.begin(9600);
  pinMode(PWMPORT_0,OUTPUT);
  pinMode(PWMPORT_1,OUTPUT);
  pinMode(PWMPORT_2,OUTPUT);
  pinMode(PWMPORT_3,OUTPUT);
  pinMode(PWMPORT_4,OUTPUT);
  pinMode(PWMPORT_5,OUTPUT);
  analogWrite(PWMPORT_0,0);
  analogWrite(PWMPORT_1,0);
  analogWrite(PWMPORT_2,0);
  analogWrite(PWMPORT_3,0);
  analogWrite(PWMPORT_4,0);
  analogWrite(PWMPORT_5,0);
  own_addr_base4 = 0x3; // 4-bit addr  hard coded or with switches
  own_addr_base8 = 0x3C; // 8-bit addr hard coded or with switches
}

void loop() {
  // check if there is 1 byte available on UART
  if(Serial.available()) {
      uint8_t d_reg = Serial.read(); // copy-read reg UDR0
      uint8_t d_key = d_reg  >> 4; // KEY 4-MSB
      uint8_t d_val = d_reg & 0x0F; // VALUE 4-LSB
      switch(fsm_state) {
        case 0: // IDLE : expected address or broadcast
          if(d_key==KCODE_ADDR4) { // addr on 4 bit
            if(d_val==own_addr_base4) { // continue listening only if 4-bit addr is own
              port_cnt=0;
              fsm_state=2;
            }  else { // wrong addr return to idle
              fsm_state=0;
            }
          } else if (d_key==KCODE_ADDR8) { // addr on 8 bit
            addr_read=d_val<<4; // SAVE 4-MSB
            fsm_state=1;
          } else if (d_reg ==KCODE_RES_BRD) { // broadcast
            port_cnt=0;
            fsm_state=2;
          } else {
            fsm_state=0;
          }
          break;
        case 1: // 2nd packet base 8 addr
          if(d_key==KCODE_ADDR8) { // 2nd part or violation and return to reset
            addr_read+=d_val;
            if(addr_read==own_addr_base8) {
              port_cnt=0;
              fsm_state=2;
            } else {
              fsm_state=0;
            }
          } else {
            fsm_state=0;
          }
          break;
        case 2: // wait for data or command
          if(d_key==KCODE_DATA4) { // DATA 4-BIT
            if (port_cnt<MAX_PORTS) { // write only if PORT is valid, extra data ignored
              uint8_t datamsb = d_val<<4;
              data_read[port_cnt]=datamsb+d_val; // data is 4-MSB and 
            }
            port_cnt++;
            fsm_state=2; // wait for new command
          } else if (d_key==KCODE_DATA8) { // DATA 8-BIT
            data_read[port_cnt]=d_val<<4; // SAVE 4-MSB
            fsm_state=3;  // wait second part of data
          } else if (d_reg ==KCODE_RES_UPD) { // update
            // update reg to port procedure
            analogWrite(PWMPORT_0,data_read[0]);
            analogWrite(PWMPORT_1,data_read[1]);
            analogWrite(PWMPORT_2,data_read[2]);
            analogWrite(PWMPORT_3,data_read[3]);
            analogWrite(PWMPORT_4,data_read[4]);
            analogWrite(PWMPORT_5,data_read[5]);
            fsm_state=2;
          } else if (d_reg ==KCODE_RES_OFF) { // power OFF
            // power off procedure
            analogWrite(PWMPORT_0,0);
            analogWrite(PWMPORT_1,0);
            analogWrite(PWMPORT_2,0);
            analogWrite(PWMPORT_3,0);
            analogWrite(PWMPORT_4,0);
            analogWrite(PWMPORT_5,0);
            fsm_state=2;
          } else if (d_reg ==KCODE_RES_END) { // EXIT
            fsm_state=0;
          }
            else {
            fsm_state=0;
          }
          break;
      case 3: // 2nd packet base 8 data
          if(d_key==KCODE_DATA8) {
            data_read[port_cnt]+=d_val; // SAVE 4-MSB
            port_cnt++;
            fsm_state=2;  // wait for other data
          } else {
            fsm_state=0;
          }
          break;
      }
  }

}
