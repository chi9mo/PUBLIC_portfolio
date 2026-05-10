/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   radix_sort.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/04 06:54:47 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:41:20 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static int	get_num_of_bit(int size)
{
	int	bit;
	int	max_index;

	bit = 0;
	max_index = size - 1;
	while (max_index > 0)
	{
		max_index >>= 1;
		bit++;
	}
	return (bit);
}

void	radix_sort(t_stack *a, t_stack *b)
{
	int	max_bit;
	int	size;
	int	i;
	int	j;

	max_bit = get_num_of_bit(a->size);
	i = 0;
	while (i < max_bit)
	{
		size = a->size;
		j = 0;
		while (j < size)
		{
			if (((a->top->index >> i) & 1) == 0)
				pb(a, b);
			else
				ra(a);
			j++;
		}
		while (b->size > 0)
			pa(a, b);
		i++;
	}
}
