/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   check_error.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/19 07:45:45 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 07:41:47 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	check_int_overflow(char *str)
{
	long	num;

	num = ft_atol(str);
	if (num < INT_MIN || num > INT_MAX)
	{
		ft_printf("Error\n(overflow)");
		return (0);
	}
	return (1);
}

static int	is_valid_integer(char *str)
{
	int	i;

	i = 0;
	if (str[i] == '-' || str[i] == '+')
		i++;
	if (!str[i])
	{
		ft_printf("Error\n(isn't valid integer)");
		return (0);
	}
	while (str[i])
	{
		if (!ft_isdigit(str[i]))
		{
			ft_printf("Error\n(isn't valid integer)");
			return (0);
		}
		i++;
	}
	return (1);
}

int	check_duplication(int *array, int size)
{
	int	i;
	int	j;

	i = 0;
	while (i < (size - 1))
	{
		j = i + 1;
		while (j < size)
		{
			if (array[i] == array[j])
			{
				ft_printf("Error\n(dup)");
				return (0);
			}
			j++;
		}
		i++;
	}
	return (1);
}

int	validate_args(char **argv, int count)
{
	int	i;

	i = 0;
	while (i < count)
	{
		if (!is_valid_integer(argv[i]) || !check_int_overflow(argv[i]))
			return (0);
		i++;
	}
	return (1);
}
