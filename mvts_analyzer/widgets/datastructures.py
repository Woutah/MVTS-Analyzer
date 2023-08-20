from __future__ import annotations
import logging
log = logging.getLogger(__name__)
#pylint: disable=missing-function-docstring

class LimitedValue():
	"""Denotes a limited value (with min/max) and a current value

	If min_val is None, min is not enforced
	If max_val is None, max is not enforced

	When setting min/max individually, min should always be smaller than max and vice versa.


	"""

	def __init__(self, min_val = None, max_val = None, val = None):
		super(LimitedValue, self).__init__()
		if val is None:
			val = min_val
		self._min_val = min_val
		self._max_val = max_val
		self._val = val
		# self.right_val

	@property
	def min_val(self):
		return self._min_val

	@min_val.setter
	def min_val(self, value):
		if value is None:
			self._min_val = None
			return
		if value != self._min_val:
			if self.max_val is None:
				self._min_val = value
			else:
				self._min_val = min(self.max_val, value)
			if self.val is None:
				return
			self.val = max(value, self.val) #Enforce new min_val

	@property
	def max_val(self):
		return self._max_val

	@max_val.setter
	def max_val(self, value):
		if value is None:
			self._max_val = None
			return
		if value != self._max_val:
			if self.min_val is None:
				self._max_val = value
			else:
				self._max_val = max(self.min_val, value)
			if self.val is None:
				return
			self.val = min(value, self.val)

	@property
	def val(self):
		return self._val

	@val.setter
	def val(self, value):
		if value != self.val:
			# self._val = max(self.min_val, min(value, self.max_val)) #make sure it is in-bound
			self._val = self.find_bounded(value)
			# self.changed.emit(self)

	def find_bounded(self, value):
		if self.max_val is not None:
			if value is None or value > self.max_val:
				return self.max_val

		if self.min_val is not None:
			if value is None or value < self.min_val:
				return self.min_val
		return value

	def __str__(self):
		return f"({self.min_val} <=) {self.val} (<= {self.max_val})"





# class LimitedRange(QtCore.QObject):
class LimitedRange():
	"""Small datastructure for rangeslider with min/max and 2 sliders
	"""

	# changed = QtCore.Signal(object)

	def __init__(self, min_val = None, max_val = None, left_val = None, right_val = None, enforce_limits = True):
		"""Constructor

		Args:
			min_val (): minimum value
			max_val (): max value
			left_val (): left slider value
			right_val (): right slider value
		"""
		super(LimitedRange, self).__init__()
		if left_val is None:
			left_val = min_val

		if right_val is None:
			right_val = max_val

		self._min_val = min_val
		self._max_val = max_val
		self._left_val = left_val
		self._right_val = right_val


		self._enforce_limits = enforce_limits


	@property
	def enforce_limits(self):
		return self._enforce_limits

	@enforce_limits.setter
	def enforce_limits(self, enforce : bool):
		"""Whether to enforce left/right value to fall within min/max values, if turned on, left/right are immmediately updated afterwards

		Args:
			enforce (bool): Whether to enforce min/max limits
		"""

		if enforce != self._enforce_limits: #If update neccesary
			if self._enforce_limits == False:
				self._left_val, self._right_val = self.find_bounded(self.left_val, self.right_val) #Update to fall within bounds
		self._enforce_limits = enforce


	@property
	def min_val(self):
		return self._min_val

	@min_val.setter
	def min_val(self, value):
		if value != self._min_val:
			if self._enforce_limits:
				if self._max_val is None:
					self._min_val = value
				else:
					self._min_val = min(self._max_val, value)
				
				if self._left_val is not None:
					self.left_val = max(value, self._left_val)
				if self.right_val is not None:
					self.right_val = max(self._min_val, self.right_val)
			else:
				self._min_val = value
			# self.changed.emit(self)



	@property
	def max_val(self):
		return self._max_val

	@max_val.setter
	def max_val(self, value):
		if value != self._max_val:
			if self._enforce_limits:
				if self._min_val is None:
					self._max_val = value
				else:
					self._max_val = max(self._min_val, value)

				if self._left_val is not None:
					self.left_val = min(self._max_val, self._left_val)
				if self._right_val is not None:
					self.right_val = min(self._max_val, self._right_val)
				# self.changed.emit(self)
			else:
				self._max_val = value

	@property
	def left_val(self):
		return self._left_val

	@left_val.setter
	def left_val(self, value):
		if value != self.left_val:
			if self._enforce_limits:
				leftnew, rightnew = self.find_bounded(value, self.right_val)
				self._left_val = leftnew
				self.right_val = rightnew #Update right as well (if neccesary)
			else:
				self._left_val = value
			# self.changed.emit(self)

	@property
	def right_val(self):
		return self._right_val

	@right_val.setter
	def right_val(self, value):
		if value != self.right_val:
			if self._enforce_limits:
				leftnew, rightnew = self.find_bounded(self.left_val, value)
				self._right_val = rightnew
				self.left_val = leftnew #Update left as well (If neccesary)
			else:
				self._right_val = value

			# self.changed.emit(self)
			# self._right_val = max(self.right_val, max(self.min_val, min(value, self.max_val))) #make sure it is in-bound
			# self.changed.emit(self)

	def __str__(self):
		return f"({self.min_val} <=) {self.left_val} <= {self.right_val} (<= {self.max_val})"


	def get_type(self):
		"""Returns the type of the limitedRange, None is returned if only None values are stored or in case of mixed types
		"""
		cur_type = type(None)
		changes = 0
		log.debug(f"Limrange values: {self}")
		if self._min_val is not None and not isinstance(self._min_val, cur_type):
			cur_type = type(self._min_val)
			changes += 1
		if self._max_val is not None and not isinstance(self._max_val, cur_type):
			cur_type = type(self._max_val)
			changes += 1
		if self._left_val is not None and not isinstance(self._left_val, cur_type):
			cur_type = type(self._left_val)
			changes += 1
		if self._right_val is not None and not isinstance(self._right_val, cur_type):
			cur_type = type(self._right_val)
			changes += 1

		log.debug(f"Curtype of limrange is now{cur_type}")

		if changes > 1: #If multiple type --> return nonetype
			return type(None)

		return cur_type

	def check_in_bounds(self, left_val = None, right_val = None):
		"""Checks whether the given left_val/right_val are valid (in the range - inclusive)
		None is unconsidered, so None, None would return True!

		Args:
			left_val ([type], optional): The left value to be checked. Defaults to None.
			right_val ([type], optional): The right value to be checked. Defaults to None.

		Returns:
			bool: wether in bounds
		"""

		if self._max_val != None and right_val != None and (right_val > self._max_val or right_val < self.min_val):
			return False
		if self._min_val != None and left_val != None and (left_val < self._min_val or left_val > self._max_val):
			return False

		return True

	def find_bounded(self, left_val=None, right_val=None, none_to_limit = True):
		"""Find the bounded left/right values based on the current max and the passed desired left and right value

		Args:
			left_val ([type], optional): The desired left value. Defaults to None.
			right_val ([type], optional): The desired right value. Defaults to None.
			none_to_limit (bool, optional): Whether "None" should be transled to the current min (left value) or current max (right value). Defaults to True.

		This assument min and max values are valid (Either one is None or (min < max) )
		"""

		if none_to_limit:
			if left_val is None:
				left_val = self.min_val
			if right_val is None:
				right_val = self.max_val


		final_values = { 'left': left_val, 'right': right_val }

		for key, val in final_values.items(): #Limit both by left and right
			if self._min_val is not None and val is not None:
				final_values[key] = max(self._min_val, final_values[key]) #type: ignore (None check is done)
			if self._max_val is not None and val is not None:
				final_values[key] = min(self._max_val, final_values[key]) #type: ignore 

		if final_values['left'] is not None and final_values['right'] is not None:
			if final_values['left'] > final_values['right']:
				final_values['left'] = final_values['right']


		return ([final_values['left'], final_values['right']])
		# if left_val > right_val:
		# 	final_values[0]
		# if right_val < left_val:


	def copy_limits(self, limrange : LimitedRange):
		"""Copies the limits of another LimitedRange, if update_vals_after is true, the current left/right values will be updated
		to fall between the new min/max values

		Args:
			limrange (LimitedRange): The LimitedRange for which the min/max values will be copies
			update_vals_after (bool, optional): Whether to update left/right to fall between min/max (and before/after eachother). Defaults to True.
		"""

		self._min_val = limrange.min_val
		self._max_val = limrange.max_val
		self.left_val, self.right_val = self.find_bounded(self.left_val, self.right_val)

	def copy_vals(self, limrange : LimitedRange):
		self.left_val , self.right_val = self.find_bounded(limrange.left_val, limrange.right_val)
		#  = left
		# self.right_val = right


	def find_factor(self, val) -> float | None:
		"""Find the factor of the given value (e.g. 0.5 = 50% of total range), returns None if min/max are not both set"""
		if self.min_val is None or self.max_val is None:
			return None
		else:
			return (val-self.min_val) / (self.max_val - self.min_val)

	@property
	def factors(self) -> tuple:
		"""Return the factors of the left and right value (e.g. 0.5 = 50% of total range)"""
		if self.min_val is None or self.max_val is None:
			return (None, None)
		elif self.max_val == self.min_val: #If exactly the same
			return (0, 1.0)
		else:
			return (
						(self.left_val-self.min_val) / (self.max_val - self.min_val),
						(self.right_val-self.min_val) / (self.max_val - self.min_val)
			)




