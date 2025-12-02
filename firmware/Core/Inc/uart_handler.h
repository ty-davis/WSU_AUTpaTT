/*
 * uart_handler.h
 *
 *  Created on: Apr 1, 2025
 *      Author: tydav
 */

#ifndef INC_UART_HANDLER_H_
#define INC_UART_HANDLER_H_

#include "stm32l0xx_hal.h"

#define MSG_HEADER_SIZE 3
#define MAX_MSG_SIZE 256


typedef enum {
	STATE_IDLE,
	STATE_RECEIVING,
	STATE_PROCESS
} UART_State_t;

void UART_StartReceiving(void);
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart);


#endif /* INC_UART_HANDLER_H_ */
