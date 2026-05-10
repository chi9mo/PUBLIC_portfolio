/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   sa.c                                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/11 16:47:52 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/12 06:41:28 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	sa(t_stack *a)
{
	t_node	*first;
	t_node	*second;

	if (!a->top || a->size < 2)
		return ;
	first = a->top;
	second = a->top->next;
	first->next = second->next;
	if (second->next)
		second->next->prev = first;
	else
		a->bottom = first;
	second->prev = NULL;
	second->next = first;
	a->top = second;
	ft_printf("sa\n");
}
