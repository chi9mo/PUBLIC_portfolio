/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/11/08 20:44:26 by diwamoto          #+#    #+#             */
/*   Updated: 2025/11/19 15:02:17 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static void	store_int(long long n, int digits, char *result, int is_negative)
{
	result[digits] = '\0';
	if (n == 0)
		result[0] = '0';
	else
	{
		while (n != 0)
		{
			result[digits - 1] = n % 10 + '0';
			n = n / 10;
			digits--;
		}
		if (is_negative)
			result[0] = '-';
	}
}

static int	count_digits(long long n)
{
	int	result;

	if (n == 0)
		return (1);
	result = 0;
	while (n != 0)
	{
		n = n / 10;
		result++;
	}
	return (result);
}

char	*ft_itoa(int n)
{
	char		*result;
	int			digits;
	int			is_negative;
	long long	llong_n;

	llong_n = n;
	is_negative = 0;
	digits = 0;
	if (llong_n < 0)
	{
		digits++;
		llong_n = -llong_n;
		is_negative = 1;
	}
	digits = digits + count_digits(llong_n);
	result = malloc(digits + 1);
	if (result == NULL)
		return (NULL);
	store_int(llong_n, digits, result, is_negative);
	return (result);
}
