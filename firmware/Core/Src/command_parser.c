/*
 * command_parser.c
 *
 *  Created on: Apr 1, 2025
 *      Author: tydav
 */

#include "stm32l0xx_hal.h"
#include "system_state.h"
#include "uart_handler.h"
#include "motor_controls.h"

extern UART_HandleTypeDef huart2;

enum status
{
    GET_STATE = 16,   // 0x10
    MOVE_AZM_BY = 17,    // 0x11
    MOVE_AZM_TO = 18,    // 0x12
    MOVE_ELV_BY = 19,    // 0x13
    MOVE_ELV_TO = 20,    // 0x14
    MOVE_TO = 21,        // 0x15
    GET_SPEED = 32,      // 0x20
    SET_AZM_SPEED = 33,  // 0x21
    SET_ELV_SPEED = 34,  // 0x22
    SET_SPEED = 35,      // 0x23
    DANCE = 36,          // 0x24
    SET_AZM_TOOTH = 64,  // 0x40
    GET_AZM_TOOTH = 65,  // 0x41
    SET_ELV_TOOTH = 66,  // 0x42
    GET_ELV_TOOTH = 67,  // 0x43
    SET_AZM_STEP = 80,   // 0x50
    GET_AZM_STEP = 81,   // 0x51
    SET_ELV_STEP = 82,   // 0x52
    GET_ELV_STEP = 83,   // 0x53
    READY = 0,           // 0x0
    CALIBRATE = 1,       // 0x1
	TOGGLE_LOCK = 2,     // 0x2
};

enum response
{
    OK_PAYLOAD = 16,    // 0x10
    OK = 32,            // 0x20
    BUSY = 48,          // 0x30
    BAD_REQUEST = 64,   // 0x40
    BAD_STEP_VAL = 65,  // 0x41
    INTL_ERROR = 80,    // 0x50
};


uint8_t hb(uint16_t val) { return (uint8_t)((val >> 8) & 0xFF); }
uint8_t lb(uint16_t val) { return (uint8_t)(val & 0xFF); }

uint32_t uint_from_arr(uint8_t *arr, uint32_t num_bytes) {
	uint32_t result = 0;
	for (int i=0; i < num_bytes; i++) {
		result += arr[i] << (num_bytes - i - 1) * 8;
	}
	return result;
}

void uint_to_arr(uint8_t *dest, uint32_t val, uint8_t size) {
	for (int i=0; i<size; i++) {
		dest[i] = val >> (size - i - 1) * 8;
	}
}


void transmit_error(uint8_t error) {
	uint8_t response[50];
	uint8_t response_len;

	response[0] = error;
	response_len = 1;
	HAL_UART_Transmit(&huart2, response, response_len, 100);
	return;
}

uint32_t motors_busy() {
	return azm_motor_state.motor_count | elv_motor_state.motor_count;
}

uint8_t good_step_value(uint16_t step_val) {
	uint16_t good_step_values[] = {200, 400, 800, 1600, 3200, 6400};
	uint8_t result = 0;
	for (int i = 0; i < sizeof(good_step_values)/sizeof(uint16_t); i++) {
		result = (step_val == good_step_values[i]) ? 1 : result;
	}
	return result;
}

void ParseCommand(uint8_t *message, uint8_t length) {
	uint8_t status = message[0];
	uint8_t version = message[1];
	uint8_t msg_length = message[2];
	uint8_t response[50];
	uint8_t response_len;

	uint16_t tooth_ratio;
	uint16_t motor_pulse_rev;


	// some debug stuff
//	uint8_t uart_buf[50];
//	uart_buf[0] = status;
//	uart_buf[1] = msg_length;
//	uart_buf[2] = length;
//	uint8_t uart_buf_len = 3;
//	uint8_t uart_buf_len = sprintf(uart_buf, "%d", msg_length, length);
//	HAL_UART_Transmit(&huart2, uart_buf, uart_buf_len, 100);




	if (version != 0 || length - MSG_HEADER_SIZE != msg_length) {
		transmit_error(BAD_REQUEST);
		return;
	}

	// respond if busy except in special cases
	switch (status) {
		case GET_STATE:
		case GET_SPEED:
		case GET_AZM_TOOTH:
		case GET_ELV_TOOTH:
		case GET_AZM_STEP:
		case GET_ELV_STEP:
		case MOVE_AZM_BY:
		case MOVE_ELV_BY:
		case MOVE_AZM_TO:
		case MOVE_ELV_TO:
			break;
		default:
			if (motors_busy()) {
				response[0] = BUSY;
				response_len = 1;
				HAL_UART_Transmit(&huart2, response, response_len, 100);
				return;
			}
			break;
	}


	switch (status) {
		case READY:
			response[0] = OK;
			response_len = 1;
			break;
		case CALIBRATE:
			azm_motor_state.motor_position = 0;
			elv_motor_state.motor_position = 0;
			response[0] = OK;
			response_len = 1;
			break;
		case TOGGLE_LOCK:
			uint8_t new_enable = azm_motor_state.motor_enable ? 0 : 1;
			set_motor_enable(&azm_motor_state, new_enable);
			set_motor_enable(&elv_motor_state, new_enable);
			response[0] = OK;
			response_len = 1;
			break;
		case GET_STATE:
			response[0] = OK_PAYLOAD;
			uint_to_arr(&response[1], azm_motor_state.motor_position, 4);
			uint_to_arr(&response[5], elv_motor_state.motor_position, 4);
//			response[1] = hb(azm_motor_state.motor_position); // we need to pass all four of these suckers
//			response[2] = lb(azm_motor_state.motor_position);
//			response[3] = hb(elv_motor_state.motor_position);
//			response[4] = lb(elv_motor_state.motor_position);
			response[9] = (uint8_t)(azm_motor_state.motor_enable | elv_motor_state.motor_enable);
			response_len = 10;
			break;
		case MOVE_AZM_BY:
			if (azm_motor_state.motor_count) {
				response[0] = BUSY;
				response_len = 1;
				break;
			}
			move_motor_by(uint_from_arr(&message[3], 4), &azm_motor_state);
			response[0] = OK;
			response_len = 1;
			break;
		case MOVE_ELV_BY:
			if (elv_motor_state.motor_count) {
				response[0] = BUSY;
				response_len = 1;
				break;
			}
			move_motor_by(uint_from_arr(&message[3], 4), &elv_motor_state);
			response[0] = OK;
			response_len = 1;
			break;
		case MOVE_AZM_TO:
			if (azm_motor_state.motor_count) {
				response[0] = BUSY;
				response_len = 1;
				break;
			}
			move_motor_to(uint_from_arr(&message[3], 4), &azm_motor_state);
			response[0] = OK;
			response_len = 1;
			break;
		case MOVE_ELV_TO:
			if (elv_motor_state.motor_count) {
				response[0] = BUSY;
				response_len = 1;
				break;
			}
			move_motor_to(uint_from_arr(&message[3], 4), &elv_motor_state);
			response[0] = OK;
			response_len = 1;
			break;
		case GET_SPEED: // TODO: FINISH
			response[0] = OK_PAYLOAD;
			break;
		case GET_AZM_TOOTH:
			response[0] = OK_PAYLOAD;
			response[1] = hb(azm_motor_state.tooth_ratio);
			response[2] = lb(azm_motor_state.tooth_ratio);
			response_len = 3;
			break;
		case SET_AZM_TOOTH:
			tooth_ratio = (uint16_t)((message[3] << 8) | message[4]);
			azm_motor_state.tooth_ratio = tooth_ratio;
			response[0] = OK;
			response_len = 1;
			break;
		case GET_ELV_TOOTH:
			response[0] = OK_PAYLOAD;
			response[1] = hb(elv_motor_state.tooth_ratio);
			response[2] = lb(elv_motor_state.tooth_ratio);
			response_len = 3;
			break;
		case SET_ELV_TOOTH:
			tooth_ratio = (uint16_t)((message[3] << 8) | message[4]);
			elv_motor_state.tooth_ratio = tooth_ratio;
			response[0] = OK;
			response_len = 1;
			break;
		case GET_AZM_STEP:
			response[0] = OK_PAYLOAD;
			response[1] = hb(azm_motor_state.motor_pulse_rev);
			response[2] = lb(elv_motor_state.motor_pulse_rev);
			response_len = 3;
			break;
		case SET_AZM_STEP:
			motor_pulse_rev = (uint16_t)((message[3] << 8) | message[4]);
			if (!good_step_value(motor_pulse_rev)) {
				transmit_error(BAD_STEP_VAL);
				return;
			}
			azm_motor_state.motor_pulse_rev = motor_pulse_rev;
			response[0] = OK;
			response_len = 1;
			break;
		case GET_ELV_STEP:
			response[0] = OK_PAYLOAD;
			response[1] = hb(elv_motor_state.motor_pulse_rev);
			response[2] = lb(elv_motor_state.motor_pulse_rev);
			response_len = 3;
			break;
		case SET_ELV_STEP:
			motor_pulse_rev = (uint16_t)((message[3] << 8) | message[4]);
			if (!good_step_value(motor_pulse_rev)) {
				transmit_error(BAD_STEP_VAL);
				return;
			}
			elv_motor_state.motor_pulse_rev = motor_pulse_rev;
			response[0] = OK;
			response_len = 1;
			break;
		case DANCE:
			dance();
			response[0] = OK;
			response_len = 1;
			break;
		default:
			response[0] = BAD_REQUEST;
			response_len = 1;
	}
	HAL_UART_Transmit(&huart2, response, response_len, 100);
}
