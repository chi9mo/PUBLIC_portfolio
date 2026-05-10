/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/14 08:37:44 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/20 21:44:34 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef FT_PRINTF_H
# define FT_PRINTF_H

# include <stdarg.h>
# include <unistd.h>
# include <stdlib.h>
# include <stdint.h>

# include "libft/libft.h"

int	ft_printf(const char *format, ...);
int	ft_printf_char(va_list ap);
int	ft_printf_str(va_list ap);
int	ft_printf_vptr(va_list ap);
int	ft_printf_unsigned_d(va_list ap);
int	ft_printf_decimal(va_list ap);
int	ft_printf_hexlower(va_list ap);
int	ft_printf_hexupper(va_list ap);

#endif
