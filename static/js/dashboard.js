$(document).ready(function () {
    // Initialize currentViewMode with the current value of the dropdown
    var currentViewMode = $('#spots-dropdown').val();

    // Function to update the icon based on bookmark status
    function updateSaveIcon($icon, isSaved) {
        if (isSaved || (currentViewMode === 'saved' && !$icon.data('unsaved'))) {
            $icon.removeClass('fa-regular').addClass('fa-solid');
        } else {
            $icon.removeClass('fa-solid').addClass('fa-regular');
        }
    }

    // check and update each save icon on page load
    $('.save-spot-icon').each(function () {
        let $icon = $(this);
        let spotId = $icon.data('spot-id');

        // if spot is already saved
        $.ajax({
            url: '/is-spot-saved/' + spotId,
            method: 'GET',
            success: function (response) {
                updateSaveIcon($icon, response.is_saved);
            }
        });
    });

    // click event handler for saving/un-saving a spot
    $('.save-spot-icon').click(function (e) {
        e.stopPropagation(); // Prevent event from bubbling up

        let $icon = $(this);
        let spotId = $icon.data('spot-id');
        console.log("Current view mode:", currentViewMode, "Spot ID:", spotId);

        // AJAX request to save or unsave the spot
        $.ajax({
            url: '/save-spot/' + spotId,
            method: 'POST',
            success: function (response) {
                // toggle icon class based on the response
                if (currentViewMode === 'saved') {
                    $icon.data('unsaved', !response.saved);

                }
                updateSaveIcon($icon, response.saved);
                // remove spot from the list if unsaved in 'saved' view mode
            },
            // if error
            error: function (xhr, status, error) {
                alert('An error occurred: ' + error);
            }
        });
    });

    // Dropdown change event
    $('#spots-dropdown').change(function () {
        currentViewMode = $(this).val(); // Update view mode on change
        $('.save-spot-icon').each(function () {
            let $icon = $(this);
            let spotId = $icon.data('spot-id');
            // Update icon based on saved status and current view mode
            $.ajax({
                url: '/is-spot-saved/' + spotId,
                method: 'GET',
                success: function (response) {
                    updateSaveIcon($icon, response.is_saved);
                }
            });
        });
    });

    $('.delete-spot-icon').click(function (e) {
        e.stopPropagation();

        let $icon = $(this);
        let spotId = $icon.data('spot-id');
        let confirmation = confirm("Are you sure you want to delete this spot?");

        if (confirmation) {
            $.ajax({
                url: '/delete_spot/' + spotId,
                method: 'POST',
                success: function (response) {
                    if (response.deleted) {
                        $icon.closest('.list-group-item').remove();
                    }
                },
                error: function (xhr, status, error) {
                    alert('An error occurred while deleting the spot: ' + error);
                }
            });
        }
    });

});
