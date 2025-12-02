/*
 * system_state.h
 *
 *  Created on: Mar 27, 2025
 *      Author: tydav
 */

#ifndef INC_SYSTEM_STATE_H_
#define INC_SYSTEM_STATE_H_

#include "stm32l0xx_hal.h"

extern TIM_HandleTypeDef htim21;
extern TIM_HandleTypeDef htim22;

typedef struct {
	uint8_t motor_enable;      // 0 = off; 1 = on
	uint16_t motor_count;      // number of steps until destination reached, this drives the motor speed
	uint8_t motor_direction;   // 0 = cw;  1 = ccw
	uint16_t motor_pulse_rev;  // selected step ratio on TB6600 driver
	uint16_t tooth_ratio;      // driven gear / driving gear, integer is scaled by 1000, e.g. 1200 represents 1.2:1 ratio
	int32_t motor_position;    // number of steps from home, 0 is home
	TIM_HandleTypeDef htim;
} MotorState;

extern MotorState azm_motor_state;
extern MotorState elv_motor_state;



#endif /* INC_SYSTEM_STATE_H_ */
