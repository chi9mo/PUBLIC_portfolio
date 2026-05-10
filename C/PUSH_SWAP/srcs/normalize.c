/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   normalize.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/20 07:25:55 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:58:43 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

static void	assign_indices(int *values, int *sorted_values,
	int *indices, size_t count)
{
	size_t	i;
	size_t	j;

	i = 0;
	while (i < count)
	{
		j = 0;
		while (j < count)
		{
			if (values[i] == sorted_values[j])
			{
				indices[i] = j;
				break ;
			}
			j++;
		}
		i++;
	}
}

int	*normalize(int size, int *values)
{
	int	*sorted_values;
	int	*indices;

	sorted_values = malloc(size * sizeof(int));
	if (!sorted_values)
		return (NULL);
	ft_memcpy(sorted_values, values, size * sizeof(int));
	quicksort(sorted_values, 0, size - 1);
	indices = malloc(size * sizeof(int));
	if (!indices)
	{
		free(sorted_values);
		return (NULL);
	}
	assign_indices(values, sorted_values, indices, size);
	free(sorted_values);
	return (indices);
}
