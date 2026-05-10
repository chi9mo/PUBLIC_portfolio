/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   quicksort.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/27 07:50:41 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:41:08 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	swap(int *a, int *b)
{
	int	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

static int	partition(int *array, int left, int right)
{
	int	i;
	int	j;
	int	pivot;

	i = left;
	j = left;
	pivot = array[right];
	while (j < right)
	{
		if (array[j] < pivot)
		{
			swap(&array[i], &array[j]);
			i++;
		}
		j++;
	}
	swap(&array[i], &array[j]);
	return (i);
}

void	quicksort(int *array, int left, int right)
{
	int	pivot_index;

	if (left < right)
	{
		pivot_index = partition(array, left, right);
		quicksort(array, left, pivot_index - 1);
		quicksort(array, pivot_index + 1, right);
	}
}
