/* 
 * Original code based on the project hid-data example by Christian Starkjohann
 * License: GNU GPL v3 
 */

/*
This example should run on most AVRs with only little changes. No special
hardware resources except INT0 are used. You may have to change usbconfig.h for
different I/O pins for USB. Please note that USB D+ must be the INT0 pin, or
at least be connected to INT0 as well.
*/

#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>  /* for sei() */
#include <util/delay.h>     /* for _delay_ms() */
#include <avr/eeprom.h>

#include <avr/pgmspace.h>   /* required by usbdrv.h */
#include "usbdrv.h"
#include "oddebug.h"        /* This is also an example for using debug macros */

enum height_data_pos {
  HEIGHT_DATA_FLAG = 0,

  HEIGHT_DATA_ADC_H,
  HEIGHT_DATA_ADC_L,

  HEIGHT_DATA_CAP_SENSE_RISE_HH,
  HEIGHT_DATA_CAP_SENSE_RISE_H,
  HEIGHT_DATA_CAP_SENSE_RISE_L,
  HEIGHT_DATA_CAP_SENSE_RISE_TIMER1_H,
  HEIGHT_DATA_CAP_SENSE_RISE_TIMER1_L,

  HEIGHT_DATA_CAP_SENSE_FALL_HH,
  HEIGHT_DATA_CAP_SENSE_FALL_H,
  HEIGHT_DATA_CAP_SENSE_FALL_L,
  HEIGHT_DATA_CAP_SENSE_FALL_TIMER1_H,
  HEIGHT_DATA_CAP_SENSE_FALL_TIMER1_L,

  HEIGHT_DATA_CAP_SENSE_COUNTER,
  HEIGHT_DATA_CAP_SENSE_OVF,

  HEIGHT_DATA_DEBUG,

  HEIGHT_DATA_COUNTER_HH,
  HEIGHT_DATA_COUNTER_H,
  HEIGHT_DATA_COUNTER_L



};

volatile unsigned char usb_rx_flag;

enum cap_sense_state_enum {
  CAP_SENSE_STATE_RISE = 1,
  CAP_SENSE_STATE_HI,
  CAP_SENSE_STATE_FALL,
  CAP_SENSE_STATE_LO,
  CAP_SENSE_STATE_STOP
};

volatile unsigned char cap_sense_state;
volatile unsigned char cap_sense_state_ready;
volatile unsigned char time_rise_l, time_rise_h, time_rise_hh;
volatile unsigned char time_fall_l, time_fall_h, time_fall_hh;
volatile unsigned char time_counter_l, time_counter_h;

/* ------------------------------------------------------------------------- */
/* ----------------------------- USB interface ----------------------------- */
/* ------------------------------------------------------------------------- */

#define BUFFER_DATA_LENGTH 128
static unsigned char height_data[BUFFER_DATA_LENGTH];
static unsigned char height_data_ready;
static unsigned char message_data[BUFFER_DATA_LENGTH];


PROGMEM char usbHidReportDescriptor[22] = {    /* USB report descriptor */
    0x06, 0x00, 0xff,              // USAGE_PAGE (Generic Desktop)
    0x09, 0x01,                    // USAGE (Vendor Usage 1)
    0xa1, 0x01,                    // COLLECTION (Application)
    0x15, 0x00,                    //   LOGICAL_MINIMUM (0)
    0x26, 0xff, 0x00,              //   LOGICAL_MAXIMUM (255)
    0x75, 0x08,                    //   REPORT_SIZE (8)
    0x95, 0x80,                    //   REPORT_COUNT (128)
    0x09, 0x00,                    //   USAGE (Undefined)
    0xb2, 0x02, 0x01,              //   FEATURE (Data,Var,Abs,Buf)
    0xc0                           // END_COLLECTION
};
/* Since we define only one feature report, we don't use report-IDs (which
 * would be the first byte of the report). The entire report consists of 128
 * opaque data bytes.
 */

/* The following variables store the status of the current data transfer */
static uchar    bytesRemaining;

/* ------------------------------------------------------------------------- */

/* usbFunctionRead() is called when the host requests a chunk of data from
 * the device. For more information see the documentation in usbdrv/usbdrv.h.
 */
uchar   usbFunctionRead(uchar *data, uchar len) {
  unsigned char i;
  if (len > bytesRemaining) len = bytesRemaining;
  for (i=0; i<len; i++) 
    data[i] = height_data[ i + BUFFER_DATA_LENGTH - bytesRemaining ];
  bytesRemaining -= len;
  return len;
}

/* usbFunctionWrite() is called when the host sends a chunk of data to the
 * device. For more information see the documentation in usbdrv/usbdrv.h.
 */
uchar usbFunctionWrite(uchar *data, uchar len) {
  unsigned char i;
  if(len > bytesRemaining)
      len = bytesRemaining;
  for (i=0; i<len; i++) 
    message_data[ BUFFER_DATA_LENGTH - bytesRemaining + i ] = data[i];
  bytesRemaining -= len;
  if (bytesRemaining == 0) return 1;
  return 0;

}

/* ------------------------------------------------------------------------- */

usbMsgLen_t usbFunctionSetup(uchar data[8]) {
  usbRequest_t    *rq = (void *)data;

  if((rq->bmRequestType & USBRQ_TYPE_MASK) == USBRQ_TYPE_CLASS){    /* HID class request */
      if(rq->bRequest == USBRQ_HID_GET_REPORT){  /* wValue: ReportType (highbyte), ReportID (lowbyte) */
          /* since we have only one report type, we can ignore the report-ID */
          bytesRemaining = 128;
          return USB_NO_MSG;  /* use usbFunctionRead() to obtain data */
      }
      else if(rq->bRequest == USBRQ_HID_SET_REPORT){
          /* since we have only one report type, we can ignore the report-ID */
          bytesRemaining = 128;
          return USB_NO_MSG;  /* use usbFunctionWrite() to receive data from host */
      }
  }else{
      /* ignore vendor type requests, we don't use any */
  }
  return 0;
}

/* ------------------------------------------------------------------------- */

static unsigned char continuity;
static unsigned char adc_flag;
ISR(ADC_vect)
{
  continuity = 0;
  if(ADCH < 128)
    continuity = 1;

  height_data[ HEIGHT_DATA_ADC_H ] = ADCH;
  height_data[ HEIGHT_DATA_ADC_L ] = ADCL;

}


/* ------------------------------------------------------------------------- */

volatile unsigned char ovf;

ISR(TIMER1_OVF_vect)
{


  // DEBUG
  height_data[ HEIGHT_DATA_DEBUG ] |= 1;

  if ( !(++height_data[ HEIGHT_DATA_COUNTER_L ]) &&
       !(++height_data[ HEIGHT_DATA_COUNTER_H ]) &&
       !(++height_data[ HEIGHT_DATA_COUNTER_HH ]) )
  {
  }

  ovf = 0;

  if (cap_sense_state == CAP_SENSE_STATE_LO )
  {

    // DEBUG
    height_data[ HEIGHT_DATA_DEBUG ] |= 64;

    if ( !(++time_counter_l) )
      cap_sense_state_ready = 1;

  }
  else if (cap_sense_state == CAP_SENSE_STATE_RISE )
  {

    // DEBUG
    height_data[ HEIGHT_DATA_DEBUG ] |= 2;

    if ( !(++time_rise_l) )
      ovf = 1;

    // continuity ?
    if (ovf == 1)
      height_data[ HEIGHT_DATA_CAP_SENSE_OVF ] |= 1;

  }
  else if (cap_sense_state == CAP_SENSE_STATE_HI )
  {

    // DEBUG
    height_data[ HEIGHT_DATA_DEBUG ] |= 128;

    if ( !(++time_counter_l) )
      cap_sense_state_ready = 1;

  }
  else if (cap_sense_state == CAP_SENSE_STATE_FALL )
  {

    // DEBUG
    height_data[ HEIGHT_DATA_DEBUG ] |= 4;

    if ( !(++time_rise_l) )
      ovf = 1;

    if (ovf == 1)
      height_data[ HEIGHT_DATA_CAP_SENSE_OVF ] |= 2;

  }


}

/* ------------------------------------------------------------------------- */

ISR(PCINT1_vect)
{
  
  if ( cap_sense_state == CAP_SENSE_STATE_RISE )
  {

    height_data[ HEIGHT_DATA_CAP_SENSE_RISE_TIMER1_L  ] = TCNT1L;
    height_data[ HEIGHT_DATA_CAP_SENSE_RISE_TIMER1_H  ] = TCNT1H;
    height_data[ HEIGHT_DATA_CAP_SENSE_RISE_HH ] = time_rise_hh;
    height_data[ HEIGHT_DATA_CAP_SENSE_RISE_H  ] = time_rise_h;
    height_data[ HEIGHT_DATA_CAP_SENSE_RISE_L  ] = time_rise_l;
    cap_sense_state_ready = 1;

    //DEBUG
    height_data[ HEIGHT_DATA_DEBUG ] |= 16;

  }
  else if ( cap_sense_state == CAP_SENSE_STATE_FALL )
  {

    height_data[ HEIGHT_DATA_CAP_SENSE_FALL_TIMER1_L  ] = TCNT1L;
    height_data[ HEIGHT_DATA_CAP_SENSE_FALL_TIMER1_H  ] = TCNT1H;
    height_data[ HEIGHT_DATA_CAP_SENSE_FALL_HH ] = time_fall_hh;
    height_data[ HEIGHT_DATA_CAP_SENSE_FALL_H  ] = time_fall_h;
    height_data[ HEIGHT_DATA_CAP_SENSE_FALL_L  ] = time_fall_l;
    cap_sense_state_ready = 1;

    //DEBUG
    height_data[ HEIGHT_DATA_DEBUG ] |= 32;

  }

  //DEBUG
  height_data[ HEIGHT_DATA_DEBUG ] |= 8;

}



/* ------------------------------------------------------------------------- */

int main(void) {
  uchar   i;

  cap_sense_state = CAP_SENSE_STATE_STOP;

  height_data_ready = 1;
  continuity = 0;

  adc_flag = 0;

  wdt_enable(WDTO_1S);
  /* Even if you don't use the watchdog, turn it off here. On newer devices,
   * the status of the watchdog (on/off, period) is PRESERVED OVER RESET!
   */
  /* RESET status: all port bits are inputs without pull-up.
   * That's the way we need D+ and D-. Therefore we don't need any
   * additional hardware initialization.
   */
  usbInit();
  usbDeviceDisconnect();  /* enforce re-enumeration, do this while interrupts are disabled! */
  i = 0;
  while(--i)
  {                       /* fake USB disconnect for > 250 ms */
    wdt_reset();
    _delay_ms(1);
  }

  /* ADC init */
  DDRB |= 0x06;
  // neuter adc for now while we test timer1/pcint1
  /*
  ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // Set ADC prescaler to 128 
  ADMUX |= (1<<REFS0) | (1<<ADLAR); // Left adjust ADC result to allow easy 8 bit reading, c0
  ADCSRA |= (1 << ADATE);  // free running source?
  ADCSRA |= (1 << ADEN);  // Enable ADC 
  ADCSRA |= (1 << ADIE);  // Enable ADC Interrupt 
  */

  /* ... */
  usbDeviceConnect();

  /* TIMER1 init */
  TCCR1A = 0x00;
  TCCR1B = 0x00;

  TIMSK1  = ( 1 << TOIE1 );
  TCCR1B |= ( 1 << CS10  );

  TCNT1H = 0;
  TCNT1L = 0;

  time_rise_l = 0;
  time_rise_h = 0;
  time_rise_hh = 0;

  time_fall_l = 0;
  time_fall_h = 0;
  time_fall_hh = 0;


  /* PCINT on PC0 */
  PCICR |= _BV(PCIE1);
  PCMSK1 |= _BV(PCINT8);  // pinc0 

  DDRC |= (1 << PC1);

  cap_sense_state = CAP_SENSE_STATE_LO;
  cap_sense_state_ready = 0;
  time_counter_l = time_counter_h = 0;
  TCNT1H = 0;
  TCNT1L = 0;


  /* usb feedback */
  usb_rx_flag = 0;


  // DEBUG
  height_data[ HEIGHT_DATA_DEBUG ] = 0;
  height_data[ HEIGHT_DATA_COUNTER_HH ] = 0;
  height_data[ HEIGHT_DATA_COUNTER_H ] = 0;
  height_data[ HEIGHT_DATA_COUNTER_L ] = 0;

  sei();

  // neuter adc for now while we test timer1/pcint1
  /*
  ADCSRA |= (1 << ADSC);  // analog digital start conversion
  */

  for(;;)
  {                /* main event loop */

    wdt_reset();

    if ( cap_sense_state == CAP_SENSE_STATE_LO )
    {

      cli();
      if (cap_sense_state_ready)
      {
        cap_sense_state_ready = 0;
        cap_sense_state = CAP_SENSE_STATE_RISE;
        time_rise_hh = time_rise_h = time_rise_l = 0;
        TCNT1H = 0;
        TCNT1L = 0;
        PORTC |= ( 1 << PC1 );
      }
      sei();

    }
    else if ( cap_sense_state == CAP_SENSE_STATE_RISE )
    {

      cli();
      if (cap_sense_state_ready)
      {
        cap_sense_state_ready = 0;
        cap_sense_state = CAP_SENSE_STATE_HI;
      }
      sei();

    }
    else if ( cap_sense_state == CAP_SENSE_STATE_HI )
    {

      cli();
      if (cap_sense_state_ready)
      {
        cap_sense_state_ready = 0;
        cap_sense_state = CAP_SENSE_STATE_FALL;
        time_fall_hh = time_fall_h = time_fall_l = 0;
        TCNT1H = 0;
        TCNT1L = 0;
        PORTC &= ~( 1 << PC1 );
      }
      sei();

    }
    else if ( cap_sense_state == CAP_SENSE_STATE_FALL )
    {

      cli();
      if (cap_sense_state_ready)
      {
        cap_sense_state_ready = 0;
        cap_sense_state = CAP_SENSE_STATE_LO;
      }
      sei();

    }

    if(continuity) 
    {
      PORTB |= (1 << 1); // Turn on LED1 
      PORTB &= ~(1 << 2); // Turn off LED2 
      height_data_ready = 0;
      height_data[ HEIGHT_DATA_FLAG ] |= 0x01;
      height_data_ready = 1;
    }
    else
    {
      PORTB &= ~(1 << 1); // Turn off LED1 
      PORTB |= (1 << 2); // Turn on LED2 
      height_data_ready = 0;
      height_data[ HEIGHT_DATA_FLAG ] &= 0xfe;
      height_data_ready = 1;
    }


    usbPoll();

  }
  return 0;

}

/* ------------------------------------------------------------------------- */
