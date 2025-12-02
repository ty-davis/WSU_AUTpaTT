/*
 * uart_handler.c
 *
 *  Created on: Apr 1, 2025
 *      Author: tydav
 */

#include "uart_handler.h"
#include "command_parser.h"

extern UART_HandleTypeDef huart2;

UART_State_t uart_state = STATE_IDLE;
uint8_t rx_buffer[MAX_MSG_SIZE];
uint8_t msg_length = 0;

void UART_StartReceiving(void) {
	uart_state = STATE_IDLE;
	HAL_UART_Receive_IT(&huart2, rx_buffer, MSG_HEADER_SIZE);
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	if (huart->Instance != USART2) return;

	switch (uart_state) {
		case STATE_IDLE:
			msg_length = rx_buffer[2];
			if (msg_length > MAX_MSG_SIZE - MSG_HEADER_SIZE) {
				msg_length = 0;
				UART_StartReceiving();
				return;
			}
			if (msg_length == 0U) {
				ParseCommand(rx_buffer, MSG_HEADER_SIZE);
				UART_StartReceiving();
				break;
			}
			uart_state = STATE_PROCESS;
			HAL_UART_Receive_IT(&huart2, rx_buffer + MSG_HEADER_SIZE, msg_length);
			break;
		case STATE_PROCESS:
			uart_state = STATE_IDLE;
			ParseCommand(rx_buffer, MSG_HEADER_SIZE + msg_length);
			UART_StartReceiving();
			break;
		default:
			UART_StartReceiving();
			break;
	}
}
