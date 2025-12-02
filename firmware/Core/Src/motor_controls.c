/*
 * motor_controls.c
 *
 *  Created on: Apr 2, 2025
 *      Author: tydav
 */

#include "motor_controls.h"
#include "stm32l0xx_it.h"
#include "system_state.h"

extern UART_HandleTypeDef huart2;
extern TIM_HandleTypeDef htim21;
extern TIM_HandleTypeDef htim22;

void start_motor_movement(MotorState *motor_state) {
	// set the direction pin
	if (motor_state->motor_direction == 0) {
		if (motor_state == &azm_motor_state) {
			HAL_GPIO_WritePin(AZM_DIR_PORT, AZM_DIR_PIN, GPIO_PIN_RESET);
		} else if (motor_state == &elv_motor_state) {
			HAL_GPIO_WritePin(ELV_DIR_PORT, ELV_DIR_PIN, GPIO_PIN_RESET);
		}
	} else {
		if (motor_state == &azm_motor_state) {
			HAL_GPIO_WritePin(AZM_DIR_PORT, AZM_DIR_PIN, GPIO_PIN_SET);
		} else if (motor_state == &elv_motor_state) {
			HAL_GPIO_WritePin(ELV_DIR_PORT, ELV_DIR_PIN, GPIO_PIN_SET);
		}
	}

	// start the timer
	if (motor_state == &azm_motor_state) {
		HAL_TIM_Base_Start_IT(&htim21);
	} else if (motor_state == &elv_motor_state) {
		HAL_TIM_Base_Start_IT(&htim22);
	}
}

void dance() {

}

uint8_t move_motor_by(int16_t degrees, MotorState *motor_state) {
	int16_t l_degrees = degrees;
	if (l_degrees < 0) {
		l_degrees *= -1;
		motor_state->motor_direction = 1;
	} else {
		motor_state->motor_direction = 0;
	}

	uint32_t count_calc = l_degrees * motor_state->tooth_ratio;
	count_calc /= 360;
	count_calc *= motor_state->motor_pulse_rev;
	count_calc /= 100000;
	motor_state->motor_count = count_calc;

	start_motor_movement(motor_state);
	return 0;
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
	// AZIMUTH TIMER
	if (htim == &htim21) {
		HAL_GPIO_TogglePin(AZM_PUL_PORT, AZM_PUL_PIN);

		// only update counts if it is set high
		if (HAL_GPIO_ReadPin(AZM_PUL_PORT, AZM_PUL_PIN)) {
			// update the position
			if (azm_motor_state.motor_direction == 0) {
				azm_motor_state.motor_position += 6400 / azm_motor_state.motor_pulse_rev;
			} else {
				azm_motor_state.motor_position -= 6400 / azm_motor_state.motor_pulse_rev;
			}

			azm_motor_state.motor_count--;
			// stop if it has reached the number of iterations.
			if (azm_motor_state.motor_count == 0) {
				HAL_TIM_Base_Stop_IT(&htim21);
			}
		}
	}

	// ELEVATION TIMER
	if (htim == &htim22) {
		HAL_GPIO_TogglePin(ELV_PUL_PORT, ELV_PUL_PIN);

		if (HAL_GPIO_ReadPin(ELV_PUL_PORT, ELV_PUL_PIN)) {
			// update the position
			if (elv_motor_state.motor_direction == 0) {
				elv_motor_state.motor_position += 6400 / elv_motor_state.motor_pulse_rev;
			} else {
				elv_motor_state.motor_position -= 6400 / elv_motor_state.motor_pulse_rev;
			}

			elv_motor_state.motor_count--;
			// stop if it has reach the number of iterations
			if (elv_motor_state.motor_count == 0) {
				HAL_TIM_Base_Stop_IT(&htim22);
			}
		}
	}
}

