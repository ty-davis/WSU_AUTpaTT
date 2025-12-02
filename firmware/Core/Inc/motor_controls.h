/*
 * motor_controls.h
 *
 *  Created on: Apr 2, 2025
 *      Author: tydav
 */

#ifndef INC_MOTOR_CONTROLS_H_
#define INC_MOTOR_CONTROLS_H_

#include "stm32l0xx_hal.h"
#include "system_state.h"

// azimuth motor
#define AZM_PUL_PORT  GPIOA
#define AZM_PUL_PIN   GPIO_PIN_8

#define AZM_DIR_PORT  GPIOB
#define AZM_DIR_PIN   GPIO_PIN_10

#define AZM_EN_PORT   GPIOB
#define AZM_EN_PIN    GPIO_PIN_4

// elevation motor
#define ELV_PUL_PORT  GPIOB
#define ELV_PUL_PIN   GPIO_PIN_5

#define ELV_DIR_PORT  GPIOB
#define ELV_DIR_PIN   GPIO_PIN_3

#define ELV_EN_PORT   GPIOA
#define ELV_EN_PIN    GPIO_PIN_10

uint8_t move_motor_by(int16_t, MotorState*);
void dance();



#endif /* INC_MOTOR_CONTROLS_H_ */
