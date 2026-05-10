/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rra.c                                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/11 17:10:05 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/11 17:10:37 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	rra(t_stack *a)
{
	t_node	*tmp;

	if (!a->top || a->size <= 1)
		return ;
	tmp = a->bottom;
	a->bottom = a->bottom->prev;
	a->bottom->next = NULL;
	tmp->prev = NULL;
	tmp->next = a->top;
	a->top->prev = tmp;
	a->top = tmp;
	ft_printf("rra\n");
}
