/* Name: main.c
 * Project: hid-data, example how to use HID for data transfer
 * Author: Christian Starkjohann
 * Creation Date: 2008-04-11
 * Tabsize: 4
 * Copyright: (c) 2008 by OBJECTIVE DEVELOPMENT Software GmbH
 * License: GNU GPL v2 (see License.txt), GNU GPL v3 or proprietary (CommercialLicense.txt)
 * This Revision: $Id$
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
  //adc_flag=1;
  //ADCSRA &= ~(1 << ADIE);  // disable ADC Interrupt 

  continuity = 0;
  if(ADCH < 128)
    continuity = 1;

}


/* ------------------------------------------------------------------------- */

int main(void) {
  uchar   i;

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
  ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // Set ADC prescaler to 128 
  ADMUX |= (1<<REFS0) | (1<<ADLAR); // Left adjust ADC result to allow easy 8 bit reading 
  ADCSRA |= (1 << ADATE);  // free running source?
  ADCSRA |= (1 << ADEN);  // Enable ADC 
  ADCSRA |= (1 << ADIE);  // Enable ADC Interrupt 

  usbDeviceConnect();
  sei();

  ADCSRA |= (1 << ADSC);  // Start A2D Conversions 

  for(;;)
  {                /* main event loop */

    wdt_reset();

    if(continuity) 
    {
      PORTB |= (1 << 1); // Turn on LED1 
      PORTB &= ~(1 << 2); // Turn off LED2 
      height_data_ready = 0;
      height_data[0] = 0xff;
      height_data_ready = 1;
    }
    else
    {
      PORTB &= ~(1 << 1); // Turn off LED1 
      PORTB |= (1 << 2); // Turn on LED2 
      height_data_ready = 0;
      height_data[0] = 0x00;
      height_data_ready = 1;
    }

    //if (adc_flag==1) {
      //adc_flag=0;
      //ADCSRA |= (1 << ADSC);  // Start A2D Conversions 
    //}

    usbPoll();

  }
  return 0;

}

/* ------------------------------------------------------------------------- */
