/*
*
The MIT License (MIT)

Copyright (c) 2014 David Qin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*
* */

(function ($) {

    // a case insensitive jQuery :contains selector
    $.expr[":"].searchableSelectContains = $.expr.createPseudo(function (arg) {
        return function (elem) {
            return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
        };
    });

    $.searchableSelect = function (element, options) {
        this.element = element;
        this.options = options || {};
        this.init();

        var _this = this;

        this.searchableElement.click(function (event) {
            // event.stopPropagation();
            _this.show();
        }).on('keydown', function (event) {
            if (event.which === 13 || event.which === 40 || event.which == 38) {
                event.preventDefault();
                _this.show();
            }
        });

        $(document).on('click', null, function (event) {
            if (_this.searchableElement.has($(event.target)).length === 0)
                _this.hide();
        });

        this.input.on('keydown', function (event) {
            event.stopPropagation();
            if (event.which === 13) {         //enter
                event.preventDefault();
                _this.selectCurrentHoverItem();
                _this.hide();
            } else if (event.which == 27) { //ese
                _this.hide();
            } else if (event.which == 40) { //down
                _this.hoverNextItem();
            } else if (event.which == 38) { //up
                _this.hoverPreviousItem();
            }
        }).on('keyup', function (event) {
            if (event.which != 13 && event.which != 27 && event.which != 38 && event.which != 40)
                _this.filter();
        })
    };

    var $sS = $.searchableSelect;

    $sS.fn = $sS.prototype = {
        version: '0.0.1'
    };

    $sS.fn.extend = $sS.extend = $.extend;

    $sS.fn.extend({
        init: function () {
            var _this = this;
            this.element.hide();

            this.searchableElement = $('<div tabindex="0" class="searchable-select"></div>');
            this.holder = $('<div class="searchable-select-holder"></div>');
            this.dropdown = $('<div class="searchable-select-dropdown searchable-select-hide"></div>');
            this.input = $('<input type="text" class="searchable-select-input" />');
            this.items = $('<div class="searchable-select-items"></div>');
            this.caret = $('<span class="searchable-select-caret"></span>');

            this.scrollPart = $('<div class="searchable-scroll"></div>');
            this.hasPrivious = $('<div class="searchable-has-privious">...</div>');
            this.hasNext = $('<div class="searchable-has-next">...</div>');

            this.hasNext.on('mouseenter', function () {
                _this.hasNextTimer = null;

                var f = function () {
                    var scrollTop = _this.items.scrollTop();
                    _this.items.scrollTop(scrollTop + 20);
                    _this.hasNextTimer = setTimeout(f, 50);
                }

                f();
            }).on('mouseleave', function (event) {
                clearTimeout(_this.hasNextTimer);
            });

            this.hasPrivious.on('mouseenter', function () {
                _this.hasPriviousTimer = null;

                var f = function () {
                    var scrollTop = _this.items.scrollTop();
                    _this.items.scrollTop(scrollTop - 20);
                    _this.hasPriviousTimer = setTimeout(f, 50);
                }

                f();
            }).on('mouseleave', function (event) {
                clearTimeout(_this.hasPriviousTimer);
            });

            this.dropdown.append(this.input);
            this.dropdown.append(this.scrollPart);

            this.scrollPart.append(this.hasPrivious);
            this.scrollPart.append(this.items);
            this.scrollPart.append(this.hasNext);

            this.searchableElement.append(this.caret);
            this.searchableElement.append(this.holder);
            this.searchableElement.append(this.dropdown);
            this.element.after(this.searchableElement);

            this.buildItems();
            this.setPriviousAndNextVisibility();
            try {
                get_data_example();
            }
            catch (err) {
            }

        },

        filter: function () {
            var text = this.input.val();
            this.items.find('.searchable-select-item').addClass('searchable-select-hide');
            this.items.find('.searchable-select-item:searchableSelectContains(' + text + ')').removeClass('searchable-select-hide');
            if (this.currentSelectedItem.hasClass('searchable-select-hide') && this.items.find('.searchable-select-item:not(.searchable-select-hide)').length > 0) {
                this.hoverFirstNotHideItem();
            }

            this.setPriviousAndNextVisibility();
        },

        hoverFirstNotHideItem: function () {
            this.hoverItem(this.items.find('.searchable-select-item:not(.searchable-select-hide)').first());
        },

        selectCurrentHoverItem: function () {
            if (!this.currentHoverItem.hasClass('searchable-select-hide'))
                this.selectItem(this.currentHoverItem);
        },

        hoverPreviousItem: function () {
            if (!this.hasCurrentHoverItem())
                this.hoverFirstNotHideItem();
            else {
                var prevItem = this.currentHoverItem.prevAll('.searchable-select-item:not(.searchable-select-hide):first')
                if (prevItem.length > 0)
                    this.hoverItem(prevItem);
            }
        },

        hoverNextItem: function () {
            if (!this.hasCurrentHoverItem())
                this.hoverFirstNotHideItem();
            else {
                var nextItem = this.currentHoverItem.nextAll('.searchable-select-item:not(.searchable-select-hide):first')
                if (nextItem.length > 0)
                    this.hoverItem(nextItem);
            }
        },

        buildItems: function () {
            var _this = this;
            this.element.find('option').each(function () {
                var item = $('<div class="searchable-select-item" data-value="' + $(this).attr('value') + '">' + escapeChars($(this).text()) + '</div>');

                if (this.selected) {
                    _this.selectItem(item);
                    _this.hoverItem(item);
                }

                item.on('mouseenter', function () {
                    $(this).addClass('hover');
                }).on('mouseleave', function () {
                    $(this).removeClass('hover');
                }).click(function (event) {
                    event.stopPropagation();
                    _this.selectItem($(this));
                    _this.hide();
                });

                _this.items.append(item);
            });

            this.items.on('scroll', function () {
                _this.setPriviousAndNextVisibility();
            })
        },
        show: function () {
            this.dropdown.removeClass('searchable-select-hide');
            this.input.focus();
            this.status = 'show';
            this.setPriviousAndNextVisibility();
            this.dropdown.css('z-index', 1000); //打开下拉列表时调高z-index层级
        },

        hide: function () {
            if (!(this.status === 'show'))
                return;

            if (this.items.find(':not(.searchable-select-hide)').length === 0)
                this.input.val('');
            this.dropdown.addClass('searchable-select-hide');
            this.searchableElement.trigger('focus');
            this.status = 'hide';
            this.dropdown.css('z-index', 1); //关闭下拉列表时恢复z-index层级
        },

        hasCurrentSelectedItem: function () {
            return this.currentSelectedItem && this.currentSelectedItem.length > 0;
        },

        selectItem: function (item) {
            if (this.hasCurrentSelectedItem())
                this.currentSelectedItem.removeClass('selected');

            this.currentSelectedItem = item;
            item.addClass('selected');

            this.hoverItem(item);

            this.holder.text(item.text());
            var value = item.data('value');
            this.holder.data('value', value);
            this.element.val(value);

            if (this.options.afterSelectItem) {
                this.options.afterSelectItem.apply(this);
            }
            try {
                get_data_example();
            }
            catch (err) {
            }

        },

        hasCurrentHoverItem: function () {
            return this.currentHoverItem && this.currentHoverItem.length > 0;
        },

        hoverItem: function (item) {
            if (this.hasCurrentHoverItem())
                this.currentHoverItem.removeClass('hover');

            if (item.outerHeight() + item.position().top > this.items.height())
                this.items.scrollTop(this.items.scrollTop() + item.outerHeight() + item.position().top - this.items.height());
            else if (item.position().top < 0)
                this.items.scrollTop(this.items.scrollTop() + item.position().top);

            this.currentHoverItem = item;
            item.addClass('hover');
        },

        setPriviousAndNextVisibility: function () {
            if (this.items.scrollTop() === 0) {
                this.hasPrivious.addClass('searchable-select-hide');
                this.scrollPart.removeClass('has-privious');
            } else {
                this.hasPrivious.removeClass('searchable-select-hide');
                this.scrollPart.addClass('has-privious');
            }

            if (this.items.scrollTop() + this.items.innerHeight() >= this.items[0].scrollHeight) {
                this.hasNext.addClass('searchable-select-hide');
                this.scrollPart.removeClass('has-next');
            } else {
                this.hasNext.removeClass('searchable-select-hide');
                this.scrollPart.addClass('has-next');
            }
        }
    });

    $.fn.searchableSelect = function (options) {
        this.each(function () {
            var sS = new $sS($(this), options);
        });

        return this;
    };

    function escapeChars(str) {
        str = str.replace(/&/g, '&amp;');
        str = str.replace(/</g, '&lt;');
        str = str.replace(/>/g, '&gt;');
        str = str.replace(/'/g, '&acute;');
        str = str.replace(/"/g, '&quot;');
        str = str.replace(/\|/g, '&brvbar;');
        return str;
    }


})(jQuery);
